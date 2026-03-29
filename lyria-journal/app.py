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
import urllib.parse
import sys
import os

# Add the current directory to sys.path so 'auth' and 'radio_rss' can be imported
# regardless of where streamlit is run from
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from auth import get_user_id

# Initialize layout
st.set_page_config(page_title="Lyria Journal", page_icon="🎵", layout="centered")

with st.sidebar:
    st.header("Paramètres")
    debug_mode = st.checkbox("Activer le mode Debug", value=False)

# Intercept query parameters early for RSS feed
if hasattr(st, "query_params") and "rss" in st.query_params:
    from radio_rss import generate_rss
    rss_content = generate_rss()
    st.code(rss_content, language="xml")
    st.stop()

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

import json

def save_to_firebase(prompt, audio_bytes, image_bytes, mood_text, title=None, lyrics=None, is_public=False, user_id=None):
    """Saves the generated audio and metadata to Firebase Storage and Firestore."""
    if not bucket:
        raise ValueError("Firebase Storage Bucket is not configured. Set FIREBASE_STORAGE_BUCKET environment variable.")

    timestamp = str(int(time.time()))
    audio_path = f"lyria_audio/{timestamp}.mp4"
    image_path = f"lyria_images/{timestamp}.jpg" if image_bytes else None

    # Upload Audio
    audio_blob = bucket.blob(audio_path)
    audio_blob.upload_from_string(audio_bytes, content_type='audio/mp4')
    audio_url = audio_blob.public_url

    # Upload Image (if provided)
    image_url = None
    if image_bytes:
        image_blob = bucket.blob(image_path)
        image_blob.upload_from_string(image_bytes, content_type='image/jpeg')
        image_url = image_blob.public_url

    # Save Metadata to Firestore
    doc_ref = db.collection('lyria_journal').document(timestamp)
    doc_ref.set({
        'prompt': prompt,
        'mood_text': mood_text,
        'title': title,
        'lyrics': lyrics,
        'audio_url': audio_url,
        'image_url': image_url,
        'created_at': datetime.utcnow(),
        'is_public': is_public,
        'user_id': user_id,
        'likes_count': 0,
        'likes_users': [],
        'views_count': 0,
        'listens_count': 0
    })

    return doc_ref.id

def generate_music_metadata(image_data, mood_text):
    """Generates a structured prompt, title, and lyrics for Lyria 3 using Gemini."""
    prompt_instruction = """
    Analyse l'image fournie (et/ou le texte fourni s'il y en a un).
    Tu dois générer trois choses basées sur ce contexte, l'humeur et l'ambiance :
    1. "prompt": Un prompt musical détaillé en anglais (50-100 mots) pour l'API Lyria 3.
       - Genre & Era : Le style et l'époque (ex: 1980s-style synth-pop).
       - Tempo & Rhythm : La vitesse et le rythme (ex: 120 BPM).
       - Instrumentation & Texture : Les instruments et l'ambiance sonore.
       - Vocal Profile : (Optionnel) Si approprié, décrit le type de voix.
       - INCLUS DANS LE PROMPT LYRIA LES PAROLES COMPLÈTES sous la forme de balises (ex: [Verse] paroles... [Chorus] paroles...). Lyria accepte les paroles directement dans le prompt musical.
    2. "title": Un titre évocateur et court pour la chanson (en français ou dans la langue demandée).
    3. "lyrics": Les paroles complètes formatées avec des sauts de ligne pour un affichage lisible. Si c'est une musique instrumentale (par exemple si classique), renvoie une chaîne vide ou "Instrumental".

    Tu DOIS impérativement renvoyer un objet JSON valide avec exactement ces 3 clés : "prompt", "title" et "lyrics". Ne rajoute pas de markdown autour de ta réponse JSON.
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
            response_mime_type="application/json"
        )
    )

    try:
        data = json.loads(response.text)
        return data.get("prompt", mood_text), data.get("title", "Sans titre"), data.get("lyrics", "")
    except Exception as e:
        print(f"Error parsing Gemini JSON: {e}")
        return mood_text, "Génération en erreur", ""

def generate_music(prompt, debug_mode=False):
    """Calls the Lyria 3 API to generate music from the prompt."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    # Lyria 3 only supports 'global' location
    if project_id:
        lyria_client = genai.Client(vertexai=True, project=project_id, location="global")
    else:
        lyria_client = client

    interaction = lyria_client.interactions.create(
        model="lyria-3-pro-preview",
        input=prompt
    )

    if debug_mode:
        st.write("Debug: Raw Interaction Response:", interaction)

    if interaction and hasattr(interaction, 'outputs') and interaction.outputs:
        for output in interaction.outputs:
            if output.type == "audio":
                return base64.b64decode(output.data)

    return None

def main():
    st.title("Lyria Journal 🎵")
    st.markdown("Votre journal intime musical et visuel.")

    tab_create, tab_public, tab_radio = st.tabs(["Créer une chanson", "Galerie Publique", "Radio"])

    with tab_create:
        st.header("Capturez votre Daily Mood")

        img_method = st.radio("Méthode pour l'image (Optionnel)", ["Prendre une photo", "Uploader une image", "Pas d'image"], index=2)

        image_data = None
        if img_method == "Prendre une photo":
            image_data = st.camera_input("Prenez une photo")
        elif img_method == "Uploader une image":
            image_data = st.file_uploader("Choisissez une image", type=["png", "jpg", "jpeg"])

        mood_text = st.text_input("Ajoutez un court texte ou légende (ex: Matinée difficile) - Optionnel")

        # Genres prédéfinis
        st.write("Genres musicaux (Optionnel)")
        available_genres = [
            "Joyeux", "Mélancolique",
            "Chanson française", "Chanson en anglais", "Pop rock",
            "Hard rock", "Heavy metal", "Hip-hop", "Slam",
            "Électro", "Jazz", "Musique classique"
        ]

        # Streamlit >= 1.40 supports st.pills for this exact use case
        if hasattr(st, "pills"):
            selected_genres = st.pills(
                "Sélectionnez un ou plusieurs genres",
                options=available_genres,
                selection_mode="multi"
            )
        else:
            selected_genres = st.multiselect(
                "Sélectionnez un ou plusieurs genres",
                options=available_genres,
                default=[]
            )

        if st.button("Générer ma musique avec Lyria"):
            if image_data is not None or mood_text or selected_genres:
                with st.spinner("Analyse de l'humeur par Gemini..."):

                    # Construct full mood text including genres
                    genres_text = f"Genres souhaités : {', '.join(selected_genres)}." if selected_genres else ""
                    full_mood_text = f"{mood_text}\n{genres_text}".strip()
                    try:
                        # Always call Gemini to generate the title and prompt (and lyrics)
                        lyria_prompt, generated_title, generated_lyrics = generate_music_metadata(image_data, full_mood_text)

                        if debug_mode:
                            st.write("Debug: Génération Gemini Prompt:", lyria_prompt)
                            st.write("Debug: Génération Gemini Titre:", generated_title)

                        st.success("Instructions musicales et titre générés !")

                        with st.spinner(f"Création de la musique '{generated_title}' par Lyria 3 (cela peut prendre quelques instants)..."):
                            audio_bytes = generate_music(lyria_prompt, debug_mode)

                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp4")
                                # Publish automatically
                                with st.spinner("Publication dans la Galerie Publique..."):
                                    try:
                                        user_id = get_user_id()
                                        save_to_firebase(
                                            prompt=lyria_prompt,
                                            audio_bytes=audio_bytes,
                                            image_bytes=image_data.getvalue() if image_data else None,
                                            mood_text=full_mood_text,
                                            title=generated_title,
                                            lyrics=generated_lyrics,
                                            is_public=True,
                                            user_id=user_id
                                        )
                                        st.success(f"Musique '{generated_title}' générée et publiée dans la Galerie Publique !")
                                        if generated_lyrics:
                                            with st.expander("📝 Paroles générées"):
                                                st.text(generated_lyrics)
                                    except Exception as e:
                                        st.error(f"Erreur lors de la publication: {e}")

                            else:
                                st.error("Aucun audio généré par Lyria. (Aucune piste audio dans la réponse)")
                    except Exception as e:
                        st.error(f"Une erreur s'est produite: {e}")
                        if debug_mode:
                            import traceback
                            st.code(traceback.format_exc())
            else:
                st.warning("Veuillez prendre une photo, ajouter une description ou sélectionner un genre pour générer votre musique.")

    with tab_public:
        st.header("Galerie Publique")
        st.write("Écoutez les créations de la communauté.")

        user_id = get_user_id()

        try:
            public_entries = db.collection('lyria_journal').where('is_public', '==', True).order_by('created_at', direction=firestore.Query.DESCENDING).limit(20).stream()
            count = 0
            for entry in public_entries:
                count += 1
                data = entry.to_dict()
                doc_id = entry.id

                # Increment view count in backend (in a real app, do this more carefully to avoid quota issues)
                if f"viewed_{doc_id}" not in st.session_state:
                    st.session_state[f"viewed_{doc_id}"] = True
                    try:
                        db.collection('lyria_journal').document(doc_id).update({
                            'views_count': firestore.Increment(1)
                        })
                    except Exception:
                        pass

                with st.container():
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if data.get('image_url'):
                            st.image(data['image_url'], width=150)
                    with col2:
                        title = data.get('title', 'Sans titre')
                        st.subheader(f"🎵 {title}")
                        st.write(f"**Posté le:** {data['created_at'].strftime('%Y-%m-%d %H:%M')}")
                        if data.get('mood_text'):
                            st.write(f"**Contexte/Mood:** {data['mood_text']}")

                        lyrics = data.get('lyrics')
                        if lyrics:
                            with st.expander("📝 Paroles"):
                                st.text(lyrics)

                        if debug_mode:
                            with st.expander("🛠️ Prompt Lyria Brut"):
                                st.write(data['prompt'])

                        # Listen count
                        listens = data.get('listens_count', 0)
                        views = data.get('views_count', 0)

                        col_listen_btn, col_stats = st.columns([1, 1])

                        with col_listen_btn:
                            if st.button("Écouter 🎧", key=f"listen_{doc_id}"):
                                st.session_state[f"playing_{doc_id}"] = True
                                # Increment listens
                                try:
                                    db.collection('lyria_journal').document(doc_id).update({
                                        'listens_count': firestore.Increment(1)
                                    })
                                    listens += 1
                                except Exception:
                                    pass

                        with col_stats:
                            st.caption(f"👁️ {views} | 🎧 {listens}")

                        if st.session_state.get(f"playing_{doc_id}", False):
                            st.audio(data['audio_url'])

                        # Like button
                        likes_users = data.get('likes_users', [])
                        has_liked = user_id in likes_users
                        likes_count = data.get('likes_count', 0)

                        col_like, col_share = st.columns([1, 1])

                        with col_like:
                            like_label = f"❤️ J'aime ({likes_count})" if not has_liked else f"💖 Aimé ({likes_count})"
                            if st.button(like_label, key=f"like_{doc_id}"):
                                try:
                                    doc_ref = db.collection('lyria_journal').document(doc_id)
                                    if has_liked:
                                        # Unlike
                                        doc_ref.update({
                                            'likes_count': firestore.Increment(-1),
                                            'likes_users': firestore.ArrayRemove([user_id])
                                        })
                                    else:
                                        # Like
                                        doc_ref.update({
                                            'likes_count': firestore.Increment(1),
                                            'likes_users': firestore.ArrayUnion([user_id])
                                        })
                                    st.rerun()
                                except Exception as e:
                                    st.error("Erreur lors du vote.")

                        with col_share:
                            import urllib.parse
                            share_text = "Découvrez mon mood du moment avec cette chanson : "
                            share_url = data['audio_url']
                            encoded_text = urllib.parse.quote(share_text + share_url)
                            whatsapp_link = f"https://api.whatsapp.com/send?text={encoded_text}"

                            st.markdown(
                                f'<a href="{whatsapp_link}" target="_blank" style="text-decoration:none;">'
                                f'<div style="text-align:center; padding: 5px; background-color: #25D366; color: white; border-radius: 5px; cursor: pointer;">'
                                f'WhatsApp 💬</div></a>',
                                unsafe_allow_html=True
                            )

                    st.divider()
            if count == 0:
                st.info("Aucune création publique trouvée.")
        except Exception as e:
            st.error(f"Erreur d'accès à la base de données : {e}")
            st.info("Avez-vous configuré les index Firestore nécessaires ?")

    with tab_radio:
        st.header("Radio Lyria 📻")
        st.write("Écoutez les 10 dernières créations à la suite.")

        try:
            radio_entries = db.collection('lyria_journal').where('is_public', '==', True).order_by('created_at', direction=firestore.Query.DESCENDING).limit(10).stream()

            playlist_items = []
            for entry in radio_entries:
                data = entry.to_dict()
                audio_url = data.get('audio_url')
                if audio_url:
                    title = data.get('title') or data.get('mood_text') or "Création sans titre"
                    image = data.get('image_url') or ""
                    # Escape quotes in title
                    title = title.replace("'", "\\'").replace('"', '\\"')
                    playlist_items.append(f"{{ title: '{title}', url: '{audio_url}', image: '{image}' }}")

            if playlist_items:
                js_playlist = ",\n".join(playlist_items)

                # HTML/JS for continuous playback
                html_code = f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; color: black;">
                    <h3 id="track-title" style="margin-bottom: 15px; color: black;">Chargement...</h3>
                    <img id="track-image" src="" style="max-height: 200px; display: none; margin: 0 auto 15px auto; border-radius: 8px;">
                    <audio id="radio-player" controls autoplay style="width: 100%;">
                        Votre navigateur ne supporte pas l'élément audio.
                    </audio>
                    <div style="margin-top: 15px;">
                        <button onclick="playNext()" style="padding: 10px 20px; background-color: #ff4b4b; color: white; border: none; border-radius: 5px; cursor: pointer;">Passer à la suivante ⏭️</button>
                    </div>
                </div>

                <script>
                    const playlist = [
                        {js_playlist}
                    ];

                    let currentIndex = 0;
                    const player = document.getElementById('radio-player');
                    const titleElement = document.getElementById('track-title');
                    const imageElement = document.getElementById('track-image');

                    function loadTrack(index) {{
                        if (index >= 0 && index < playlist.length) {{
                            const track = playlist[index];
                            player.src = track.url;
                            titleElement.innerText = "Lecture : " + track.title;

                            if (track.image) {{
                                imageElement.src = track.image;
                                imageElement.style.display = "block";
                            }} else {{
                                imageElement.style.display = "none";
                            }}

                            player.play().catch(e => console.log("Auto-play prevented:", e));
                        }}
                    }}

                    function playNext() {{
                        currentIndex++;
                        if (currentIndex >= playlist.length) {{
                            currentIndex = 0; // Loop back to start
                        }}
                        loadTrack(currentIndex);
                    }}

                    // Event listener for when a song ends
                    player.addEventListener('ended', playNext);

                    // Initial load
                    loadTrack(0);
                </script>
                """
                import streamlit.components.v1 as components
                components.html(html_code, height=450)

                # Expose a way to get the RSS link
                st.divider()
                st.write("**Flux RSS disponible :**")
                # Create a link with query param ?rss=true to self
                from radio_rss import generate_rss
                rss_xml = generate_rss()
                st.download_button(
                    label="Télécharger le flux RSS (.xml)",
                    data=rss_xml,
                    file_name="lyria_radio_rss.xml",
                    mime="application/rss+xml"
                )

                # Try to construct full URL for dynamic RSS
                try:
                    if hasattr(st, "context") and hasattr(st.context, "headers"):
                        host = st.context.headers.get("Host", "localhost:8501")
                        scheme = st.context.headers.get("X-Forwarded-Proto", "http")
                        rss_url = f"{scheme}://{host}/?rss=true"
                        st.markdown(f"Lien dynamique RSS : `[Copier ce lien]({rss_url})` (si supporté par votre hébergeur)")
                except Exception:
                    pass

            else:
                st.info("Pas assez de pistes pour lancer la radio.")

        except Exception as e:
            st.error(f"Erreur de chargement de la radio : {e}")


if __name__ == "__main__":
    main()
