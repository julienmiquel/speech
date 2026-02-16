import streamlit as st
import os
import json
import time
from gemini_url_to_audio import extract_text_from_url, extract_text_from_url_with_gemini, parse_text_structure, synthesize_multi_speaker, synthesize_and_save, convert_url_to_file_name, PROMPT_ANCHOR, PROMPT_REPORTER
from google import genai
from dotenv import load_dotenv
from storage import LocalStorage, RemoteStorage

# Load environment variables
load_dotenv()

# Setup page
st.set_page_config(page_title="Gemini TTS Workshop", layout="wide")

st.title("🎙️ Le Figaro x Gemini TTS Factory")
st.markdown("Workshop Demo: Article to Audio using Gemini 2.0 Flash & Gemini 2.5 Pro")

# Sidebar - Configuration
st.sidebar.header("Configuration")

# Credentials
if "app_mode" not in st.session_state:
    st.session_state.app_mode = os.getenv("APP_MODE", "local")

if st.session_state.app_mode == "remote":
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        st.error("Missing GOOGLE_CLOUD_PROJECT env var for remote mode.")
        st.stop()
    
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        st.error("Missing GCS_BUCKET_NAME env var for remote mode.")
        st.stop()
        
    st.sidebar.success(f"Remote Mode: {project_id}")
    
    # Initialize Storage
    # Force reload of storage class by using a new key or re-importing? 
    # Streamlit reloads modules, but instances persist.
    # We'll use 'storage_v2' to force checking for new instance if code changed
    if "storage_v2" not in st.session_state:
        st.session_state.storage_v2 = RemoteStorage(bucket_name, project_id)
else:
    project_id = st.sidebar.text_input("Google Cloud Project ID", value="customer-demo-01")
    # Initialize Storage
    if "storage_v2" not in st.session_state:
        st.session_state.storage_v2 = LocalStorage()

# Compat for rest of app
if "storage_v2" in st.session_state:
    st.session_state.storage = st.session_state.storage_v2

location = st.sidebar.text_input("Location", value="us-central1")
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

# Models
st.sidebar.subheader("Models")
model_parse = st.sidebar.selectbox("Parsing Model (Structure)", ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite-preview", "gemini-3-flash-preview"], index=0)
model_synth = st.sidebar.selectbox("Synthesis Model (Audio)", ["gemini-2.5-pro-tts", "gemini-2.5-flash-tts", "gemini-2.5-flash-lite-preview-tts"], index=0)

# Voices
st.sidebar.subheader("Voices")
# https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/pali-gemma
# Known voices: Aoede, Fenrir, Charon, Kore, Puck, Zephyr
voices_available = [
    "Achernar", "Achird", "Algenib", "Algieba", "Alnilam", 
    "Aoede", "Autonoe", "Callirrhoe", "Charon", "Despina", 
    "Encelade", "Erinome", "Fenrir", "Gacrux", "Iapetus", 
    "Kore", "Laomedeia", "Léda", "Orus", "Pulcherrima", 
    "Puck", "Rasalgethi", "Sadachbia", "Sadaltager", "Schedar", 
    "Sulafat", "Umbriel", "Vindemiatrix", "Zephyr", "Zubenelgenubi"
]

VOICE_DESCRIPTIONS = {
    "Achernar": "Female, Bubbly, Modern, Approachable (High Pitch)",
    "Achird": "Male, Friendly, Energetic (Youthful)",
    "Algenib": "Male, Deep, Baritone, Reassuring (User specified Male)", 
    "Algieba": "Male, Deep, Dynamic, Resonant",
    "Alnilam": "Male, Energetic, Commercial, 'Guy Next Door'",
    "Aoede": "Female, Professional, Clear (Good for News)",
    "Autonoe": "Female, Warm, Cheerful, Conversational (US)",
    "Callirrhoe": "Female, Polished, Warm, Helpful (Young Adult)",
    "Charon": "Male, Deep, Steady, Professional",
    "Despina": "Female, Bright, Polished, Enthusiastic",
    "Encelade": "Male, Deep, Resonant, Polished (Mature)",
    "Erinome": "Female, Bright, Crisp, Youthful",
    "Fenrir": "Male, Deep, Authoritative (Good for Narration)",
    "Gacrux": "Female, Standard Voice",
    "Iapetus": "Male, Standard Voice",
    "Kore": "Female, Calm, Soothing",
    "Laomedeia": "Female, Standard Voice",
    "Léda": "Female, Standard Voice",
    "Orus": "Male, Standard Voice",
    "Pulcherrima": "Female, Standard Voice",
    "Puck": "Male, Energetic, Playful",
    "Rasalgethi": "Male, Standard Voice",
    "Sadachbia": "Male, Lively, Professional",
    "Sadaltager": "Male, Standard Voice",
    "Schedar": "Male, Energetic, Upbeat, Conversational",
    "Sulafat": "Female, Standard Voice",
    "Umbriel": "Male, Friendly, Casual, Upbeat",
    "Vindemiatrix": "Female, Standard Voice",
    "Zephyr": "Female, Gentle, Soft",
    "Zubenelgenubi": "Male, Standard Voice"
}

voice_main = st.sidebar.selectbox("Main Voice (Narrator)", voices_available, index=5) # Aoede
st.sidebar.caption(f"ℹ️ {VOICE_DESCRIPTIONS.get(voice_main, '')}")

voice_sidebar = st.sidebar.selectbox("Sidebar Voice (Encarts)", voices_available, index=12) # Fenrir
st.sidebar.caption(f"ℹ️ {VOICE_DESCRIPTIONS.get(voice_sidebar, '')}")

with st.sidebar.expander("Voice Details"):
    st.write(VOICE_DESCRIPTIONS)

import glob

# Navigation
nav = st.sidebar.radio("Navigation", ["Generator", "Playground", "History"], index=0)

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ... existing code ...

def render_generator():
    # Presets from tts_requirements.md
    presets = {
        "Custom URL": "",
        "Long Article (Quotes + Enrichments)": "https://www.lefigaro.fr/politique/j-ai-pris-la-decision-d-etre-candidat-de-la-place-beauvau-a-la-conquete-de-l-elysee-la-mue-presidentielle-de-bruno-retailleau-20260212",
        "Editorial": "https://www.lefigaro.fr/vox/economie/l-editorial-de-gaetan-de-capele-strategie-energetique-il-faut-sanctuariser-le-nucleaire-20260211",
        "Economy (Figures)": "https://www.lefigaro.fr/conjoncture/l-industrie-automobile-francaise-a-perdu-un-tiers-de-ses-effectifs-entre-2010-et-2023-constate-l-insee-20260212",
        "Interview (Q&A)": "https://www.lefigaro.fr/musique/lord-kossity-le-rap-c-est-un-art-et-la-jeune-generation-fait-tout-sauf-du-rap-20260211",
        # "International (Foreign Names)": "https://www.lefigaro.fr/international/le-pentagone-prepare-le-deploiement-d-un-deuxieme-porte-avions-pour-accroitre-la-pression-sur-l-iran-selon-le-wall-street-journal-20260212",
        "Brands (Shein)": "https://www.lefigaro.fr/conso/les-plateformes-d-ultra-fast-fashion-seduisent-toujours-plus-d-un-francais-sur-trois-en-2025-d-apres-une-etude-20260212"
    }

    selected_preset = st.selectbox("Load Example Article", list(presets.keys()))

    if "url_input" not in st.session_state:
        st.session_state.url_input = "https://www.lefigaro.fr/meteo/meteo-decouvrez-les-16-departements-places-en-vigilance-orange-crues-ou-pluie-inondation-ce-11-fevrier-20260210"

    # Update session state if preset changes (and isn't Custom)
    if selected_preset != "Custom URL":
         st.session_state.url_input = presets[selected_preset]

    # Main Area
    url = st.text_input("Article URL", key="url_input")
    
    # State Management: Clear previous processing if URL changes
    if "last_url" not in st.session_state:
        st.session_state.last_url = ""
        
    if url != st.session_state.last_url:
        logging.info(f"URL changed from '{st.session_state.last_url}' to '{url}'. Clearing extraction/analysis state.")
        st.session_state.last_url = url
        st.session_state.text_content = ""
        if "dialogue" in st.session_state:
            del st.session_state.dialogue
    
    default_system_prompt = """You are an expert content analyzer.
Analyze the following article text. Identify the main narrative text and any RELEVANT 'encarts' (e.g. quotes, important explanatory boxes).
Exlude any content that corresponds to:
- Navigation menus
- Links/URLs not part of the narrative
- Irrelevant sidebars or ads

Output a JSON list of objects, where each object represents a continuous segment of text.
Each object must have:
- "text": The exact text content of the segment.
- "type": "main" for main article text, or "sidebar" for relevant encarts.

Maintain the original reading order.
"""

    if "text_content" not in st.session_state:
        st.session_state.text_content = ""

    if "history" not in st.session_state:
        st.session_state.history = []

    st.subheader("1. Extraction")
    extraction_method = st.radio("Méthode", [f"{model_parse} (Smart)", "BeautifulSoup (Standard)"], index=0, horizontal=True)
    with st.expander("Paramètres de Parsing", expanded=False):
        strict_mode = st.checkbox("Mode Strict (Aucun changement de mot)", value=True)


        system_prompt = st.text_area("System Prompt (Parsing)", value=default_system_prompt, height=300)
        
    if st.button("Extraire le Texte"):
        logging.info(f"Starting extraction for URL: {url} using method: {extraction_method}")
        with st.spinner(f"Extraction en cours via {extraction_method}..."):
                if "gemini" in extraction_method.lower():
                    text = extract_text_from_url_with_gemini(url, parsing_model=model_parse)
                else:
                    text = extract_text_from_url(url)
                    
                if text:
                    logging.info(f"Extraction successful. Length: {len(text)} chars.")
                    st.session_state.text_content = text
                    st.success(f"Extrait {len(text)} caractères.")
                else:
                    logging.error("Extraction failed.")
                    st.error("Échec de l'extraction.")

    if st.session_state.text_content:
        st.text_area("Texte Extrait (Aperçu)", st.session_state.text_content, height=200)

        if st.button("2. Analyser la Structure"):
            if not st.session_state.text_content:
                st.error("Veuillez d'abord extraire le texte.")
            else:
                with st.spinner("Analyse de la structure avec Gemini..."):
                    # Construct full prompt based on UI + Strict Mode logic
                    final_prompt = system_prompt
                    if strict_mode:
                        final_prompt += """
        CRITICAL: STRICT MODE ENABLED.
        - Do NOT change a single word of the original text.
        - Do NOT add any pauses, vocal tags, or extra punctuation.
        - Do NOT remove any text unless it is clearly navigation/menu/ad garbage.
        - The "text" field MUST match the original content EXACTLY word-for-word.
        """
                    else:
                        final_prompt += """
        IMPORTANT: To improve the reading flow, insert the following tags into the "text" content where appropriate:
        - [short pause] : Insert this tag between distinct list items or short clauses to create a natural breathing pause.
    - [medium pause] : Insert this tag between major sentences or distinct ideas.
    - [long pause] : Insert this tag before a significant topic change or dramatic statement.

    You MAY also use the following "Vocal Tags" (use sparingly, only if the text content heavily supports the emotion):
    - [curious] : Use for questions or intriguing statements.
    - [scared] : Use for frightening content.
    - [bored] : Use for monotonous content.

    CRITICAL: Ensure every "text" segment ends with a period (.) if it does not already end with a punctuation mark.

    Do NOT use these tags excessively, only where they improve the natural rhythm of a news reading.
    """


                    dialogue = parse_text_structure(st.session_state.text_content, model=model_parse, strict_mode=strict_mode, system_prompt=final_prompt)
                    
                    if dialogue:
                        st.session_state.dialogue = dialogue
                        st.success(f"Analysé {len(dialogue)} segments.")
                    else:
                        st.error("Échec de l'analyse structurelle.")

    # Ensure assets directory exists
    if not os.path.exists("assets"):
        os.makedirs("assets")

    # Helper to save metadata
    def save_metadata(outfile, mode, model_synth, voice_main, voice_sidebar, prompt_system, prompt_main, prompt_sidebar, dialogue):
        
        # If remote, we must have already uploaded the file and 'outfile' is a URL
        # If local, 'outfile' is a path
        
        meta = {
            "timestamp": int(time.time()),
            "mode": mode,
            "url": url,
            "extraction_method": extraction_method,
            "model_parse": model_parse,
            "model_synth": model_synth,
            "voice_main": voice_main,
            "voice_sidebar": voice_sidebar,
            "strict_mode": strict_mode,
            "prompts": {
                "system": prompt_system,
                "tts_main": prompt_main,
                "tts_sidebar": prompt_sidebar
            },
            "audio_file": outfile,
            "dialogue": dialogue,
            "full_text": st.session_state.text_content
        }
        
        # Save Metadata via Abstraction
        dest_key = outfile
        st.session_state.storage.save_metadata(meta, dest_key)
        
        # Add to session history
        st.session_state.history.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "mode": mode,
            "model": model_synth,
            "url": url,
            "voices": f"{voice_main} / {voice_sidebar}",
            "audio_file": outfile,
            "prompt_system": prompt_system,
            "prompt_tts_main": prompt_main,
            "prompt_tts_sidebar": prompt_sidebar
        })
        return outfile # Return the ref

    if "dialogue" in st.session_state:
        st.subheader("3. Édition & Synthèse")
        
        with st.expander("Paramètres de Prompt TTS", expanded=False):
            prompt_main = st.text_area("Prompt Speaker 1 (Principal)", value=PROMPT_ANCHOR, height=100)
            prompt_sidebar = st.text_area("Prompt Speaker 2 (Secondaire)", value=PROMPT_REPORTER, height=100)
        
        # Script Builder UI (Editable Source)
        st.markdown("### Constructeur de Script")
        dialogue = st.session_state.dialogue
        to_remove = -1
        
        for i, block in enumerate(dialogue):
            with st.container(border=True):
                c_speaker, c_remove = st.columns([4, 1])
                
                current_speaker = block.get("speaker", "R")
                idx = 0 if current_speaker == "R" else 1
                new_speaker = c_speaker.radio(f"Intervenant (Bloc {i+1})", ["Speaker 1 (Principal)", "Speaker 2 (Secondaire)"], index=idx, key=f"gen_spk_{i}", horizontal=True, label_visibility="collapsed")
                
                block["speaker"] = "R" if "Speaker 1" in new_speaker else "S"
                
                if c_remove.button("🗑️", key=f"gen_del_{i}"):
                    to_remove = i
                
                block["text"] = st.text_area(f"Texte {i+1}", value=block["text"], height=100, key=f"gen_txt_{i}", label_visibility="collapsed")
        
        if to_remove >= 0:
            dialogue.pop(to_remove)
            st.rerun()

        if st.button("⊕ Ajouter un dialogue", key="gen_add"):
            last_speaker = dialogue[-1]["speaker"] if dialogue else "S"
            next_speaker = "S" if last_speaker == "R" else "R"
            dialogue.append({"speaker": next_speaker, "text": "", "prompt": ""})
            st.rerun()

        c1, c2, c3 = st.columns(3)
        
        with c1:
            if st.button("Générer Voix Unique"):
                with st.spinner("Synthèse en cours..."):
                    # Force single speaker
                    single_dialogue = [d.copy() for d in st.session_state.dialogue]
                    for d in single_dialogue: d["speaker"] = "R"
                    
                    # Generate unique filename
                    timestamp = int(time.time())
                    outfile_name = f"assets/single_{timestamp}.wav"
                    
                    outfile = synthesize_multi_speaker(
                        single_dialogue, 
                        model=model_synth, 
                        voice_main=voice_main, 
                        voice_sidebar=voice_main,
                        output_file=outfile_name,
                        strict_mode=strict_mode,
                        prompt_main=prompt_main,
                        prompt_sidebar=prompt_sidebar
                    )
                    if outfile:
                        final_ref = outfile
                        if st.session_state.app_mode == "remote":
                            with open(outfile, "rb") as f:
                                final_ref = st.session_state.storage.save_file(f.read(), outfile)
                        
                        save_metadata(final_ref, "Single Voice (Voix Unique)", model_synth, voice_main, voice_main, system_prompt, prompt_main, prompt_sidebar, single_dialogue)
                        
                        # Play LOCAL file (outfile) for immediate feedback, ensuring no GCS latency/auth issues
                        st.audio(outfile)
                        st.success(f"Sauvegardé : {final_ref}")
                        
        with c2:
            if st.button("Générer Double Voix"):
                with st.spinner("Synthèse Double Voix..."):
                     # Generate unique filename
                     timestamp = int(time.time())
                     outfile_name = f"assets/dual_{timestamp}.wav"
    
                     outfile = synthesize_multi_speaker(
                        st.session_state.dialogue, 
                        model=model_synth, 
                        voice_main=voice_main, 
                        voice_sidebar=voice_sidebar,
                        output_file=outfile_name,
                        strict_mode=strict_mode,
                        prompt_main=prompt_main,
                        prompt_sidebar=prompt_sidebar
                    )
                     if outfile:
                        final_ref = outfile
                        if st.session_state.app_mode == "remote":
                            with open(outfile, "rb") as f:
                                final_ref = st.session_state.storage.save_file(f.read(), outfile)

                        save_metadata(final_ref, "Dual Voice (Double Voix)", model_synth, voice_main, voice_sidebar, system_prompt, prompt_main, prompt_sidebar, st.session_state.dialogue)
                        
                        # Play LOCAL file
                        st.audio(outfile)
                        st.success(f"Sauvegardé : {final_ref}")
    
        with c3:
            if st.button("Générer Comparaison (Standard)"):
                 with st.spinner("Synthèse Standard TTS..."):
                    try:
                        from gtts import gTTS
                        clean_text = " ".join(seg["text"] for seg in st.session_state.dialogue)
                        tts = gTTS(text=clean_text, lang='fr')
                        timestamp = int(time.time())
                        outfile = f"assets/standard_{timestamp}.wav"
                        tts.save(outfile)
                        
                        final_ref = outfile
                        if st.session_state.app_mode == "remote":
                            with open(outfile, "rb") as f:
                                final_ref = st.session_state.storage.save_file(f.read(), outfile)

                        save_metadata(final_ref, "Standard Comparisons", "gTTS", "Standard", "Standard", system_prompt, "N/A", "N/A", st.session_state.dialogue)
                        
                        # Play LOCAL file
                        st.audio(outfile)
                        st.success(f"Sauvegardé : {final_ref}")
                    except ImportError:
                        st.error("gTTS non installé.")

        st.markdown("---")
        st.subheader("4. Benchmark Vocal")
        if st.button("Lancer Benchmark (1er Segment pour TOUTES les voix)"):
            first_segment = [st.session_state.dialogue[0].copy()]
            # Force speaker to R
            first_segment[0]["speaker"] = "R"
            text_preview = first_segment[0]["text"][:50] + "..."
            
            st.write(f"Benchmark sur le texte : *{text_preview}*")
            
            progress_bar = st.progress(0)
            
            for i, voice in enumerate(voices_available):
                with st.spinner(f"Génération {voice}..."):
                    timestamp = int(time.time())
                    outfile_name = f"assets/benchmark_{voice}_{timestamp}.wav"
                    
                    outfile = synthesize_multi_speaker(
                        first_segment, 
                        model=model_synth, 
                        voice_main=voice, 
                        voice_sidebar=voice, # comparison is single voice
                        output_file=outfile_name,
                        strict_mode=strict_mode,
                        prompt_main=prompt_main,
                        prompt_sidebar=prompt_sidebar
                    )
                    
                    if outfile:
                        final_ref = outfile
                        if st.session_state.app_mode == "remote":
                            with open(outfile, "rb") as f:
                                final_ref = st.session_state.storage.save_file(f.read(), outfile)
                                
                        save_metadata(final_ref, "Benchmark", model_synth, voice, voice, system_prompt, prompt_main, prompt_sidebar, first_segment)
                        st.write(f"**{voice}** ({VOICE_DESCRIPTIONS.get(voice, 'Unknown')})")
                        
                        # Play LOCAL file
                        st.audio(outfile)
                        
                progress_bar.progress((i + 1) / len(voices_available))
                
            st.success("Benchmark Terminé !")

    # Existing History Section (Session Only)
    if st.session_state.history:
        st.markdown("---")
        st.subheader("Last Session Generations")
        for i, item in enumerate(st.session_state.history):
            with st.expander(f"{item['timestamp']} - {item['mode']} - {item.get('voices', 'N/A')} ({item['model']})"):
                st.write(f"**URL:** {item['url']}")
                st.audio(item['audio_file'])

def render_history():
    st.header("📜 Persistent History")
    
    if st.session_state.app_mode == "remote":
        st.info(f"Connected to Remote Storage (GCS: {os.getenv('GCS_BUCKET_NAME')}, Firestore: {os.getenv('FIRESTORE_COLLECTION', 'generations')})")
    else:
        st.info("Browsing Local Storage (assets/)")
    
    # 1. Load Data via Storage Provider
    try:
        history_items = st.session_state.storage.list_history()
    except Exception as e:
        st.error(f"Error fetching history: {e}")
        return

    if not history_items:
        st.info("No history found. Generate some audio first!")
        return

    # Normalize Loop (Optional, provider should handle most)
    normalized_items = []
    for data in history_items:
            # Handle legacy format (list of segments) if any
            if isinstance(data, list):
                 # This is tricky for remote, but we'll assume remote data is clean
                 # If local, provider handles it mostly, but let's double check
                 pass
            
            # Normalize missing fields
            if "url" not in data: data["url"] = "Unknown URL"
            if "timestamp" not in data: data["timestamp"] = 0
            
            normalized_items.append(data)
    
    history_items = normalized_items

    # 2. Group by URL
    grouped = {}
    for item in history_items:
        url = item["url"]
        
        # Special handling for Playground to group by text content
        if url == "Playground Input":
            text_preview = item.get("full_text", "")[:50].replace("\n", " ")
            if len(item.get("full_text", "")) > 50:
                text_preview += "..."
            url = f"Playground: {text_preview}"
            
        if url not in grouped:
            grouped[url] = []
        grouped[url].append(item)
    
    # 3. Sort Groups by latest timestamp
    # Get max timestamp for each group
    group_sorting = []
    for url, items in grouped.items():
        # Sort items inside group descending
        items.sort(key=lambda x: x["timestamp"], reverse=True)
        latest = items[0]["timestamp"]
        group_sorting.append((url, latest))
    
    # Sort groups descending by their latest item
    group_sorting.sort(key=lambda x: x[1], reverse=True)

    # 4. Render
    for url, _ in group_sorting:
        items = grouped[url]
        count = len(items)
        
        # Main Expander for the Article/URL
        with st.expander(f"📄 {url} ({count} versions)"):
            
            # Table Header
            c_mode, c_model, c_voices, c_date = st.columns([1, 1.5, 2, 1.5])
            c_mode.markdown("**Mode**")
            c_model.markdown("**Model**")
            c_voices.markdown("**Voices**")
            c_date.markdown("**Date**")
            st.markdown("---")
            
            for item in items:
                timestamp = item["timestamp"]
                date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                
                # Summary Row
                c1, c2, c3, c4 = st.columns([1, 1.5, 2, 1.5])
                c1.write(item.get("mode", "?"))
                c2.write(item.get("model_synth", "?"))
                c3.write(f"{item.get('voice_main', '?')} / {item.get('voice_sidebar', '?')}")
                c4.write(date_str)
                
                # Audio Player & Details
                audio_file = item.get("audio_file")
                
                # Check if we need to download it locally (Cache)
                local_path = audio_file
                if st.session_state.app_mode == "remote":
                     # In remote mode, audio_file is a URL or processed path.
                     # We want to cache it locally in assets/
                     filename = os.path.basename(audio_file)
                     local_path = os.path.join("assets", filename)
                     
                     if not os.path.exists(local_path):
                         try:
                            st.session_state.storage.download_file(audio_file, local_path)
                         except Exception as e:
                             st.warning(f"Could not download audio: {e}")
                             local_path = None
                
                if local_path and os.path.exists(local_path):
                    st.audio(local_path)
                elif audio_file:
                     # Fallback to URL if verify/download failed or not needed
                     public_url = st.session_state.storage.get_public_url(audio_file)
                     if public_url:
                        st.audio(public_url)
                else:
                    st.warning(f"Audio missing: {audio_file}")
                
                # Drill-down details
                with st.expander("Show Details (Prompts & JSON)"):
                    prompts = item.get("prompts", {})
                    st.caption("System Prompt")
                    st.text(prompts.get("system", "N/A"))
                    
                    pc1, pc2 = st.columns(2)
                    with pc1:
                        st.caption("Main Prompt")
                        st.text(prompts.get("tts_main", "N/A"))
                    with pc2:
                        st.caption("Sidebar Prompt")
                        st.text(prompts.get("tts_sidebar", "N/A"))
                        
                    st.json(item.get("dialogue"))
                
                st.markdown("---")

def render_playground():
    st.subheader("🛝 Playground (Constructeur de Script)")
    st.markdown("Construisez votre script bloc par bloc ou chargez un fichier JSON.")

    # initialize session state for playground dialogue if not exists
    if "playground_dialogue" not in st.session_state:
        st.session_state.playground_dialogue = [
            {"speaker": "R", "text": "Bonjour ! Nous sommes ravis de vous présenter nos capacités de synthèse vocale.", "prompt": ""},
            {"speaker": "S", "text": "Où vous pouvez diriger une voix, créer des dialogues réalistes, et bien plus encore.", "prompt": ""}
        ]

    # Layout: Left (JSON/Config) - Right (Visual Builder)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Code d'implémentation")
        st.caption("Ci-dessous la structure de votre script pour l'appel API.")
        
        # File Uploader
        uploaded_file = st.file_uploader("Charger un script JSON", type=["json"])
        if uploaded_file is not None:
             try:
                 data = json.load(uploaded_file)
                 if isinstance(data, list):
                     # Validate simple format
                     valid = True
                     for item in data:
                         if "text" not in item: valid = False
                     
                     if valid:
                         if st.button("Appliquer le JSON chargé"):
                             st.session_state.playground_dialogue = data
                             st.rerun()
                     else:
                         st.error("Format JSON invalide. Une liste d'objets avec le champ 'text' est attendue.")
             except Exception as e:
                 st.error(f"Erreur de chargement JSON : {e}")

        # JSON View (ReadOnly)
        st.json(st.session_state.playground_dialogue, expanded=False)


    with col2:
        st.subheader("Constructeur de Script")
        
        # Global Style Instructions
        with st.expander("Instructions de Style (System Prompt)", expanded=False):
             system_prompt_pg = st.text_area("System Prompt", value="Read aloud in a warm, welcoming tone", height=70)
        
        # Builder Container
        dialogue = st.session_state.playground_dialogue
        
        # Action to remove
        to_remove = -1
        
        for i, block in enumerate(dialogue):
            with st.container(border=True):
                c_speaker, c_remove = st.columns([4, 1])
                
                current_speaker = block.get("speaker", "R")
                idx = 0 if current_speaker == "R" else 1
                new_speaker = c_speaker.radio(f"Intervenant (Bloc {i+1})", ["Speaker 1 (Principal)", "Speaker 2 (Secondaire)"], index=idx, key=f"spk_{i}", horizontal=True, label_visibility="collapsed")
                
                block["speaker"] = "R" if "Speaker 1" in new_speaker else "S"
                
                if c_remove.button("🗑️", key=f"del_{i}"):
                    to_remove = i
                
                block["text"] = st.text_area(f"Texte {i+1}", value=block["text"], height=100, key=f"txt_{i}", label_visibility="collapsed")
        
        # Remove logic
        if to_remove >= 0:
            dialogue.pop(to_remove)
            st.rerun()
            
        # Add Dialog Button
        if st.button("⊕ Ajouter un dialogue"):
            last_speaker = dialogue[-1]["speaker"] if dialogue else "S"
            next_speaker = "S" if last_speaker == "R" else "R"
            dialogue.append({"speaker": next_speaker, "text": "", "prompt": ""})
            st.rerun()

    # 2. Synthesis Controls
    st.divider()
    st.subheader("Synthèse Audio")
    
    with st.expander("Paramètres Avancés"):
        prompt_main = st.text_area("Prompt Speaker 1", value=PROMPT_ANCHOR, height=70, key="pg_p_main")
        prompt_sidebar = st.text_area("Prompt Speaker 2", value=PROMPT_REPORTER, height=70, key="pg_p_sidebar")
        strict_mode = st.checkbox("Mode Strict", value=True, key="pg_strict")

    if st.button("Générer l'audio du script", key="pg_generate", type="primary", use_container_width=True):
        if not st.session_state.playground_dialogue:
            st.error("Le script est vide.")
        else:
             with st.spinner("Synthèse du script en cours..."):
                timestamp = int(time.time())
                outfile_name = f"assets/playground_script_{timestamp}.wav"
                
                dialogue_to_synth = st.session_state.playground_dialogue
                
                outfile = synthesize_multi_speaker(
                    dialogue_to_synth, 
                    model=model_synth, 
                    voice_main=voice_main, 
                    voice_sidebar=voice_sidebar,
                    output_file=outfile_name,
                    strict_mode=strict_mode,
                    prompt_main=prompt_main,
                    prompt_sidebar=PROMPT_REPORTER
                )
                
                if outfile:
                    final_ref = outfile
                    if st.session_state.app_mode == "remote":
                         with open(outfile, "rb") as f:
                                final_ref = st.session_state.storage.save_file(f.read(), outfile)

                    # Save metadata
                    meta = {
                        "timestamp": int(time.time()),
                        "mode": "Playground Script",
                        "url": "Playground Input",
                        "extraction_method": "Script Builder",
                        "model_parse": "N/A",
                        "model_synth": model_synth,
                        "voice_main": voice_main,
                        "voice_sidebar": voice_sidebar,
                        "strict_mode": strict_mode,
                        "prompts": {
                            "system": system_prompt_pg,
                            "tts_main": prompt_main,
                            "tts_sidebar": "N/A"
                        },
                        "audio_file": final_ref,
                        "dialogue": dialogue_to_synth,
                        "full_text": " [Script] "
                    }
                    
                    st.session_state.storage.save_metadata(meta, final_ref)

                    # Check if remote and download for playback
                    local_playback_path = final_ref
                    if st.session_state.app_mode == "remote":
                         # We just uploaded it, but st.audio might need a local file for better latency/reliability
                         # or if the bucket is not public. 
                         # 'outfile' (assets/...) is still local! checking if it exists.
                         if os.path.exists(outfile):
                             local_playback_path = outfile
                         else:
                             # Should not happen in this flow, but for robustness:
                             local_playback_path = "assets/temp_playback.wav"
                             st.session_state.storage.download_file(final_ref, local_playback_path)

                    st.audio(local_playback_path)
                    st.success(f"Généré et sauvegardé dans l'historique !")

if nav == "Generator":
    render_generator()
elif nav == "Playground":
    render_playground()
else:
    render_history()
