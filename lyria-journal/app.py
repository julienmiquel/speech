import os
import io
import time
import base64
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime

st.set_page_config(page_title="Lyria Journal", page_icon="🎵", layout="centered")

# Initialize Gemini Client
@st.cache_resource
def get_client():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_REGION", "global")
    # Will use credentials from environment if on Cloud Run
    if project_id:
        return genai.Client(vertexai=True, project=project_id, location=location)
    else:
        # Fallback to local API Key if available
        return genai.Client()

client = get_client()

# Initialize Firebase App
@st.cache_resource
def get_firebase_app():
    if not firebase_admin._apps:
        # Assuming the app runs in GCP, it uses default credentials
        # Or you can provide a credentials object
        cred = credentials.ApplicationDefault()

        # Determine the default storage bucket
        bucket_name = os.environ.get("FIREBASE_STORAGE_BUCKET")
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

        # If no bucket specified, assume the default bucket format
        if not bucket_name and project_id:
            bucket_name = f"{project_id}.appspot.com"

        options = {}
        if bucket_name:
            options['storageBucket'] = bucket_name

        return firebase_admin.initialize_app(cred, options)
    return firebase_admin.get_app()

try:
    get_firebase_app()
    db = firestore.client()
    bucket = storage.bucket() if os.environ.get("FIREBASE_STORAGE_BUCKET") or os.environ.get("GOOGLE_CLOUD_PROJECT") else None
except Exception:
    db = None
    bucket = None

def save_to_firebase(prompt, audio_bytes, image_bytes, mood_text, is_public=False):
    """Saves the generated audio and metadata to Firebase Storage and Firestore."""
    if not bucket:
        raise ValueError("Firebase Storage Bucket is not configured. Set FIREBASE_STORAGE_BUCKET environment variable.")

    timestamp = str(int(time.time()))
    audio_path = f"lyria_audio/{timestamp}.mp4"
    image_path = f"lyria_images/{timestamp}.jpg" if image_bytes else None

    # Upload Audio
    audio_blob = bucket.blob(audio_path)
    audio_blob.upload_from_string(audio_bytes, content_type='audio/mp4')
    audio_blob.make_public()
    audio_url = audio_blob.public_url

    # Upload Image (if provided)
    image_url = None
    if image_bytes:
        image_blob = bucket.blob(image_path)
        image_blob.upload_from_string(image_bytes, content_type='image/jpeg')
        image_blob.make_public()
        image_url = image_blob.public_url

    # Save Metadata to Firestore
    doc_ref = db.collection('lyria_journal').document(timestamp)
    doc_ref.set({
        'prompt': prompt,
        'mood_text': mood_text,
        'audio_url': audio_url,
        'image_url': image_url,
        'created_at': datetime.utcnow(),
        'is_public': is_public
    })

    return doc_ref.id

def generate_music_prompt(image_data, mood_text):
    """Generates a structured prompt for Lyria 3 using Gemini."""
    prompt_instruction = """
    Analyse l'image fournie (et le texte s'il y en a un).
    Génère un prompt musical détaillé en anglais (50-100 mots) pour l'API Lyria 3 basé sur l'humeur, les couleurs et le contexte.
    Structure ton prompt selon ces règles :
    1. Genre & Era : Le style et l'époque (ex: 1980s-style synth-pop, lo-fi hip hop).
    2. Tempo & Rhythm : La vitesse et le rythme (ex: 120 BPM, chill beat).
    3. Instrumentation & Texture : Les instruments et l'ambiance sonore.
    4. Vocal Profile : (Optionnel) Si approprié, décrit le type de voix.

    Renvoie UNIQUEMENT le prompt musical généré, sans aucune introduction, sans formatage markdown, juste le texte brut du prompt.
    """

    contents = []

    if image_data:
        image = Image.open(image_data)
        contents.append(image)

    if mood_text:
        contents.append(f"Texte de contexte utilisateur : {mood_text}\n\n")

    contents.append(prompt_instruction)

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.7,
        )
    )
    return response.text.strip()

def generate_music(prompt):
    """Calls the Lyria 3 API to generate music from the prompt."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    
    # Lyria 3 only supports 'global' location
    if project_id:
        lyria_client = genai.Client(vertexai=True, project=project_id, location="global")
    else:
        lyria_client = client
        
    interaction = lyria_client.interactions.create(
        model="lyria-3-clip-preview",
        input=prompt
    )

    for output in interaction.outputs:
        if output.type == "audio":
            return base64.b64decode(output.data)

    return None

def main():
    st.title("Lyria Journal 🎵")
    st.markdown("Votre journal intime musical et visuel.")

    tab_create, tab_private, tab_public = st.tabs(["Daily Mood (Create)", "Galerie Privée", "Galerie Publique"])

    with tab_create:
        st.header("Capturez votre Daily Mood")

        image_data = st.camera_input("Prenez une photo pour inspirer votre musique")
        mood_text = st.text_input("Ajoutez un court texte ou légende (ex: Matinée difficile) - Optionnel")

        if st.button("Générer ma musique avec Lyria"):
            if image_data is not None or mood_text:
                with st.spinner("Analyse de l'humeur par Gemini..."):
                    try:
                        lyria_prompt = generate_music_prompt(image_data, mood_text)
                        st.success("Prompt généré !")
                        st.markdown(f"**Prompt:** {lyria_prompt}")

                        with st.spinner("Création de la musique par Lyria 3 (cela peut prendre quelques instants)..."):
                            audio_bytes = generate_music(lyria_prompt)

                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp4")
                                st.session_state.current_generation = {
                                    "prompt": lyria_prompt,
                                    "audio": audio_bytes,
                                    "image": image_data.getvalue() if image_data else None,
                                    "mood_text": mood_text
                                }

                                st.success("Musique générée ! Vous pouvez maintenant la publier.")

                            else:
                                st.error("Aucun audio généré par Lyria.")
                    except Exception as e:
                        st.error(f"Une erreur s'est produite: {e}")
            else:
                st.warning("Veuillez prendre une photo ou ajouter une description pour générer votre musique.")

        if "current_generation" in st.session_state:
            st.divider()
            st.write("Souhaitez-vous publier ce souvenir ?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Sauvegarder en Privé"):
                    with st.spinner("Sauvegarde dans votre studio..."):
                        try:
                            save_to_firebase(
                                prompt=st.session_state.current_generation["prompt"],
                                audio_bytes=st.session_state.current_generation["audio"],
                                image_bytes=st.session_state.current_generation["image"],
                                mood_text=st.session_state.current_generation["mood_text"],
                                is_public=False
                            )
                            st.success("Sauvegardé dans votre Galerie Privée !")
                            del st.session_state.current_generation
                        except Exception as e:
                            st.error(f"Erreur lors de la sauvegarde: {e}")
            with col2:
                if st.button("Publier dans la Galerie Publique"):
                    with st.spinner("Publication dans la Galerie Publique..."):
                        try:
                            save_to_firebase(
                                prompt=st.session_state.current_generation["prompt"],
                                audio_bytes=st.session_state.current_generation["audio"],
                                image_bytes=st.session_state.current_generation["image"],
                                mood_text=st.session_state.current_generation["mood_text"],
                                is_public=True
                            )
                            st.success("Publié dans la Galerie Publique !")
                            del st.session_state.current_generation
                        except Exception as e:
                            st.error(f"Erreur lors de la publication: {e}")

    with tab_private:
        st.header("Mon Studio & Calendrier")
        st.write("Retrouvez ici votre historique de création personnel.")
        try:
            entries = db.collection('lyria_journal').where('is_public', '==', False).order_by('created_at', direction=firestore.Query.DESCENDING).limit(10).stream()
            count = 0
            for entry in entries:
                count += 1
                data = entry.to_dict()
                with st.expander(f"🎵 Souvenir du {data['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                    if data.get('image_url'):
                        st.image(data['image_url'], width=300)
                    if data.get('mood_text'):
                        st.write(f"**Mood:** {data['mood_text']}")
                    st.write(f"**Prompt:** {data['prompt']}")
                    st.audio(data['audio_url'])
            if count == 0:
                st.info("Aucun souvenir privé trouvé.")
        except Exception as e:
            st.error(f"Erreur d'accès à la base de données : {e}")
            st.info("Avez-vous configuré les index Firestore nécessaires ?")

    with tab_public:
        st.header("Galerie Publique")
        st.write("Écoutez les créations de la communauté.")
        try:
            public_entries = db.collection('lyria_journal').where('is_public', '==', True).order_by('created_at', direction=firestore.Query.DESCENDING).limit(10).stream()
            count = 0
            for entry in public_entries:
                count += 1
                data = entry.to_dict()
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if data.get('image_url'):
                            st.image(data['image_url'], width=150)
                    with col2:
                        st.write(f"**Posté le:** {data['created_at'].strftime('%Y-%m-%d %H:%M')}")
                        if data.get('mood_text'):
                            st.write(f"**Mood:** {data['mood_text']}")
                        st.write(f"**Prompt:** {data['prompt']}")
                        st.audio(data['audio_url'])
                    st.divider()
            if count == 0:
                st.info("Aucune création publique trouvée.")
        except Exception as e:
            st.error(f"Erreur d'accès à la base de données : {e}")
            st.info("Avez-vous configuré les index Firestore nécessaires ?")

if __name__ == "__main__":
    main()
