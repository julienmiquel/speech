import streamlit as st
import os
import json
import time
import wave
from gemini_url_to_audio import (
    extract_text_from_url, extract_text_from_url_with_gemini, parse_text_structure, 
    research_pronunciations, get_cached_text, save_to_cache,
    synthesize_multi_speaker, synthesize_and_save, convert_url_to_file_name, 
    synthesize_replicated_voice, 
    load_pronunciation_dictionary, update_pronunciation_dictionary, save_pronunciation_dictionary, DICTIONARY_PATH,
    DEFAULT_MODEL_PARSE, DEFAULT_MODEL_SYNTH, DEFAULT_MODEL_CLONING, DEFAULT_VOICE_MAIN, DEFAULT_VOICE_SIDEBAR
)
from prompts import (
    PROMPT_ANCHOR, PROMPT_REPORTER, 
    SYSTEM_PROMPT_STANDARD, SYSTEM_PROMPT_FIGARO_SMART
)
from google import genai
from dotenv import load_dotenv
from storage import LocalStorage, RemoteStorage

# Load environment variables
load_dotenv()

# Setup page
st.set_page_config(page_title="Gemini TTS Workshop", layout="wide")

st.title("🎙️ Le Figaro x Gemini TTS Factory")
st.markdown("Workshop Demo: Article to Audio using Gemini 2.0 Flash & Gemini 2.5 Pro")

# Ensure assets directory exists globally
if not os.path.exists("assets"):
    os.makedirs("assets")

# Initialize Token Usage
if "token_usage" not in st.session_state:
    st.session_state.token_usage = {"prompt": 0, "candidates": 0, "total": 0}

def update_token_usage(usage):
    if not usage: return
    st.session_state.token_usage["prompt"] += (usage.get("prompt_token_count") or 0)
    st.session_state.token_usage["candidates"] += (usage.get("candidates_token_count") or 0)
    st.session_state.token_usage["total"] += (usage.get("total_token_count") or 0)

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
    if "storage_v2" not in st.session_state:
        st.session_state.storage_v2 = RemoteStorage(bucket_name, project_id)
else:
    # Local Mode - use env vars directly, no UI input
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "customer-demo-01")
    # Initialize Storage
    if "storage_v2" not in st.session_state:
        st.session_state.storage_v2 = LocalStorage()

# Compat for rest of app
if "storage_v2" in st.session_state:
    st.session_state.storage = st.session_state.storage_v2

location = os.getenv("LOCATION", "europe-west9")
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

# Models
st.sidebar.subheader("Models")

parse_models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite-preview", "gemini-3-flash-preview"]
try: idx_parse = parse_models.index(DEFAULT_MODEL_PARSE)
except ValueError: idx_parse = 0
model_parse = st.sidebar.selectbox("Parsing Model (Structure)", parse_models, index=idx_parse)

synth_models = ["gemini-2.5-pro-tts", "gemini-2.5-flash-tts", "gemini-2.5-flash-lite-preview-tts"]
try: idx_synth = synth_models.index(DEFAULT_MODEL_SYNTH)
except ValueError: idx_synth = 0
model_synth = st.sidebar.selectbox("Synthesis Model (Audio)", synth_models, index=idx_synth)

# Language
st.sidebar.subheader("Language")
languages = ["fr-FR", "en-US", "en-GB", "de-DE", "es-ES"]
language = st.sidebar.selectbox("Language Code", languages, index=0)

# Voices
st.sidebar.subheader("Voices")
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

try: idx_main = voices_available.index(DEFAULT_VOICE_MAIN)
except ValueError: idx_main = 5 # Aoede
voice_main = st.sidebar.selectbox("Main Voice (Narrator)", voices_available, index=idx_main)
st.sidebar.caption(f"ℹ️ {VOICE_DESCRIPTIONS.get(voice_main, '')}")

try: idx_sidebar = voices_available.index(DEFAULT_VOICE_SIDEBAR)
except ValueError: idx_sidebar = 12 # Fenrir
voice_sidebar = st.sidebar.selectbox("Sidebar Voice (Encarts)", voices_available, index=idx_sidebar)
st.sidebar.caption(f"ℹ️ {VOICE_DESCRIPTIONS.get(voice_sidebar, '')}")

with st.sidebar.expander("Voice Details"):
    st.write(VOICE_DESCRIPTIONS)

# Token Usage Display
st.sidebar.subheader("💰 Coût & Usage")
if "token_usage" in st.session_state:
    u = st.session_state.token_usage
    st.sidebar.caption(f"Prompt: {u['prompt']} | Candidates: {u['candidates']}")
    st.sidebar.info(f"**Total Tokens: {u['total']}**")
    
# Dictionary Management
st.sidebar.subheader("Prononciation")
apply_dictionary = st.sidebar.checkbox("Activer le dictionnaire", value=True, help="Remplace les mots par leur équivalent phonétique défini plus bas.")

with st.sidebar.expander("📖 Dictionnaire de Prononciation"):
    pronunciation_dict = load_pronunciation_dictionary()
    
    # 1. Individual Entry Editor
    st.subheader("Ajouter une entrée")
    new_word = st.text_input("Mot d'origine", key="new_word_dict", placeholder="Fillon")
    new_pron = st.text_input("Prononciation", key="new_pron_dict", placeholder="Fi-yon")
    
    if st.button("➕ Ajouter", use_container_width=True):
        if new_word and new_pron:
            pronunciation_dict[new_word] = new_pron
            if save_pronunciation_dictionary(pronunciation_dict):
                st.success(f"Ajouté: {new_word}")
                st.rerun()
        else:
            st.error("Veuillez remplir les deux champs.")
            
    st.markdown("---")
    
    # 2. Bulk JSON Editor
    st.subheader("Éditeur JSON (Bulk)")
    dict_json = json.dumps(pronunciation_dict, indent=4, ensure_ascii=False)
    new_dict_json = st.text_area("JSON complet", value=dict_json, height=200)
    
    if st.button("💾 Sauvegarder le JSON", use_container_width=True):
        try:
            updated_dict = json.loads(new_dict_json)
            if save_pronunciation_dictionary(updated_dict):
                st.success("Dictionnaire mis à jour !")
                st.rerun()
        except Exception as e:
            st.error(f"Erreur JSON : {e}")

    st.markdown("---")
    
    # 3. List and delete
    st.subheader("Entrées actuelles")
    for word, pron in list(pronunciation_dict.items()):
        col_text, col_del = st.columns([4, 1])
        col_text.text(f"{word} → {pron}")
        if col_del.button("🗑️", key=f"del_dict_{word}"):
            del pronunciation_dict[word]
            if save_pronunciation_dictionary(pronunciation_dict):
                st.rerun()

import glob

# Navigation (Top Level)
st.markdown("---")
nav = st.radio("Navigation", ["🎙️ Générateur", "🧪 Test Dictionnaire", "🧬 Voice Cloning", "📜 Historique"], horizontal=True, label_visibility="collapsed")
st.markdown("---")

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ... existing code ...

import re

def sanitize_text_for_filename(text):
    """Sanitize text for use in filenames (alphanumeric only)."""
    # Replace accent chars first (simplistic)
    text = text.replace("é", "e").replace("è", "e").replace("à", "a").replace("ç", "c")
    return re.sub(r'[^a-zA-Z0-9]', '_', text).strip('_')

def render_generator():
    # Presets from tts_requirements.md
    presets = {
        "Custom URL": "",
        "Long Article (Quotes + Enrichments)": "https://www.lefigaro.fr/politique/j-ai-pris-la-decision-d-etre-candidat-de-la-place-beauvau-a-la-conquete-de-l-elysee-la-mue-presidentielle-de-bruno-retailleau-20260212",
        "Editorial": "https://www.lefigaro.fr/vox/economie/l-editorial-de-gaetan-de-capele-strategie-energetique-il-faut-sanctuariser-le-nucleaire-20260211",
        "Economy (Figures)": "https://www.lefigaro.fr/conjoncture/l-industrie-automobile-francaise-a-perdu-un-tiers-de-ses-effectifs-entre-2010-et-2023-constate-l-insee-20260212",
        "Interview (Q&A)": "https://www.lefigaro.fr/musique/lord-kossity-le-rap-c-est-un-art-et-la-jeune-generation-fait-tout-sauf-du-rap-20260211",
        "International (Foreign Names)": "https://www.lefigaro.fr/international/le-pentagone-prepare-le-deploiement-d-un-deuxieme-porte-avions-pour-accroitre-la-pression-sur-l-iran-selon-le-wall-street-journal-20260212",
        "Brands (Shein)": "https://www.lefigaro.fr/conso/les-plateformes-d-ultra-fast-fashion-seduisent-toujours-plus-d-un-francais-sur-trois-en-2025-d-apres-une-etude-20260212"
    }

    # Selection logic: Only update url_input if the preset selection actually CHANGED
    if "last_preset" not in st.session_state:
        st.session_state.last_preset = "Custom URL"

    selected_preset = st.selectbox("Load Example Article", list(presets.keys()))

    if "url_input" not in st.session_state:
        st.session_state.url_input = "https://www.lefigaro.fr/meteo/meteo-decouvrez-les-16-departements-places-en-vigilance-orange-crues-ou-pluie-inondation-ce-11-fevrier-20260210"

    # If user changed the preset, update the url_input
    if selected_preset != st.session_state.last_preset:
        st.session_state.last_preset = selected_preset
        if selected_preset != "Custom URL":
             st.session_state.url_input = presets[selected_preset]
             st.rerun()

    # Automation Button at the top for convenience
    if st.button("🚀 TOUT RÉALISER ( extraction + prononciation + structure )", use_container_width=True):
        st.session_state.run_automation = True

    # Main Area
    url = st.text_input("Article URL", key="url_input")
    
    # State Management: Clear previous processing if URL changes
    if "last_url" not in st.session_state:
        # Initialize last_url to current url to prevent clearing on first load
        st.session_state.last_url = url
        
    if url != st.session_state.last_url:
        logging.info(f"URL changed from '{st.session_state.last_url}' to '{url}'. Clearing extraction/analysis state.")
        st.session_state.last_url = url
        st.session_state.text_content = ""
        if "dialogue" in st.session_state:
            del st.session_state.dialogue
    
    system_prompts = {
        "Standard": SYSTEM_PROMPT_STANDARD,
        "Figaro Smart (Rich Content)": SYSTEM_PROMPT_FIGARO_SMART
    }
    
    default_system_prompt = system_prompts["Standard"]

    if "text_content" not in st.session_state:
        st.session_state.text_content = ""

    if "history" not in st.session_state:
        st.session_state.history = []

    if "pg_p_main" not in st.session_state:
        st.session_state.pg_p_main = PROMPT_ANCHOR
    if "pg_p_sidebar" not in st.session_state:
        st.session_state.pg_p_sidebar = PROMPT_REPORTER

    st.subheader("1. Extraire texte brut ou URL")
    extraction_method = st.radio("Méthode d'extraction", [f"{model_parse} (Smart)", "BeautifulSoup (Standard)"], index=0, horizontal=True)
    
    # Tips Section based on Feedback
    with st.expander("💡 Tips & Guide (Feedbacks Figaro)", expanded=False):
        st.markdown("""
        **Bonnes Pratiques :**
        - **Prononciation** : Les prompts incluent des guides pour "Fillon", "Retailleau", etc. Vous pouvez aussi ajouter des précisions phonétiques entre parenthèses dans le texte (ex: "80 (quatre-vingts)").
        - **Didascalies** : Utilisez des balises comme `[short pause]`, `[long pause]`, `[surprised]`, `[laughing]` directement dans le texte pour plus d'expressivité.
        - **Contenus Enrichis** : Utilisez le prompt "Figaro Smart" pour mieux gérer les descriptions d'images/vidéos.
        - **Voix** : "Speaker 1" = Voix Principale, "Speaker 2" = Voix Encarts (ex: Fenrir).
        """)

    with st.expander("Paramètres de Parsing", expanded=False):
        strict_mode = st.checkbox("Mode Strict (Aucun changement de mot)", value=True)

        system_prompt_choice = st.selectbox("System Prompt Template", list(system_prompts.keys()), index=0)
        default_system_prompt = system_prompts[system_prompt_choice]

        system_prompt = st.text_area("System Prompt (Parsing)", value=default_system_prompt, height=300)
        
    if st.button("Extraire le Texte"):
        logging.info(f"Checking cache or starting extraction for URL: {url}")
        
        # Check cache first
        cached_text = get_cached_text(url)
        if cached_text:
            st.session_state.text_content = cached_text
            st.success("Texte chargé depuis le cache local (instantané).")
        else:
            with st.spinner(f"Extraction en cours via {extraction_method}..."):
                    if "gemini" in extraction_method.lower():
                        text, usage = extract_text_from_url_with_gemini(url, parsing_model=model_parse)
                        update_token_usage(usage)
                    else:
                        text = extract_text_from_url(url)
                        
                    if text:
                        logging.info(f"Extraction successful. Length: {len(text)} chars.")
                        st.session_state.text_content = text
                        save_to_cache(url, text)
                        st.success(f"Extrait {len(text)} caractères.")
                    else:
                        logging.error("Extraction failed.")
                        st.error("Échec de l'extraction.")

    # One-Click Automation Logic
    if st.session_state.get("run_automation", False):
        st.session_state.run_automation = False # Reset
        with st.status("🛠️ Automatisation en cours...", expanded=True) as status:
            # 1. Extraction (if needed)
            if not st.session_state.text_content:
                status.update(label="1. Extraction du texte...")
                cached_text = get_cached_text(url)
                if cached_text:
                    st.session_state.text_content = cached_text
                else:
                    if "gemini" in extraction_method.lower():
                        text, usage = extract_text_from_url_with_gemini(url, parsing_model=model_parse)
                        update_token_usage(usage)
                    else:
                        text = extract_text_from_url(url)
                    if text:
                        st.session_state.text_content = text
                        save_to_cache(url, text)
            
            if st.session_state.text_content:
                # 2. Pronunciation Research
                status.update(label="2. Recherche de prononciation (Google Search)...")
                guides, usage = research_pronunciations(st.session_state.text_content, model=model_parse, language=language)
                update_token_usage(usage)
                if guides:
                    st.session_state.pronunciation_guides = guides
                    # Automatically update dictionary for new terms
                    added = update_pronunciation_dictionary(guides)
                    if added > 0:
                        st.info(f"➕ {added} nouveaux termes ajoutés au dictionnaire global.")
                    
                    guides_text = "\nConsignes de prononciation :\n" + "\n".join([f"- {g['term']} se prononce '{g['guide']}'" for g in guides])
                    st.session_state.pg_p_main += guides_text
                    st.session_state.pg_p_sidebar += guides_text
                
                # 3. Structuration
                status.update(label="3. Analyse de la structure...")
                # We use the default system prompt here for automation
                dialogue, usage = parse_text_structure(st.session_state.text_content, model=model_parse, strict_mode=st.session_state.get("strict_mode", True), system_prompt=system_prompts["Standard"])
                update_token_usage(usage)
                if dialogue:
                    st.session_state.dialogue = dialogue
            
            status.update(label="✅ Automatisation terminée !", state="complete")
        st.rerun()

    if st.session_state.text_content:
        st.text_area("Texte Extrait (Aperçu)", st.session_state.text_content, height=150)

        st.markdown("---")
        st.subheader("2. 🔍 Recherche de Prononciation")
        if st.button("Lancer la recherche (Google Search)"):
            with st.spinner("Recherche Google en cours..."):
                guides, usage = research_pronunciations(st.session_state.text_content, model=model_parse, language=language)
                update_token_usage(usage)
                if guides:
                    st.session_state.pronunciation_guides = guides
                    # Automatically update dictionary for new terms
                    added = update_pronunciation_dictionary(guides)
                    st.success(f"{len(guides)} guides de prononciation trouvés !")
                    if added > 0:
                        st.info(f"➕ {added} nouveaux termes ajoutés au dictionnaire global.")
                else:
                    st.warning("Aucun guide spécifique trouvé ou erreur de recherche.")

        if "pronunciation_guides" in st.session_state and st.session_state.pronunciation_guides:
            with st.expander("Guides de prononciation trouvés", expanded=True):
                for g in st.session_state.pronunciation_guides:
                    st.write(f"- **{g['term']}** : {g['guide']}")
                
                if st.button("Appliquer comme consignes (Prompts)"):
                    guides_text = "\nConsignes de prononciation :\n" + "\n".join([f"- {g['term']} se prononce '{g['guide']}'" for g in st.session_state.pronunciation_guides])
                    st.session_state.pg_p_main += guides_text
                    st.session_state.pg_p_sidebar += guides_text
                    st.success("Guides ajoutés aux prompts de synthèse !")
                    st.rerun()

        st.markdown("---")
        st.subheader("3. Structuration")
        show_phonetic = st.checkbox("🔍 Afficher les adaptations de prononciation (Aperçu audio)", value=False)
        if st.button("Analyser la Structure"):
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

    You MAY also use the following "Vocal Tags" (didascalies) to match the emotion of the content:
    - [curious] : Use for questions or intriguing statements.
    - [surprised] : Use for shocking or unexpected information.
    - [laughing] : Use for lighter, humorous, or ironic content.
    - [whispering] : Use for sensitive information.
    - [sigh] : Use for discouraging or heavy news.

    CRITICAL: Ensure every "text" segment ends with a period (.) if it does not already end with a punctuation mark.

    Do NOT use these tags excessively, only where they improve the natural rhythm of a news reading.
    """


                    dialogue, usage = parse_text_structure(st.session_state.text_content, model=model_parse, strict_mode=strict_mode, system_prompt=final_prompt)
                    update_token_usage(usage)
                    
                    if dialogue:
                        st.session_state.dialogue = dialogue
                        st.success(f"Analysé {len(dialogue)} segments.")
                    else:
                        st.error("Échec de l'analyse structurelle.")

    # Step 4 is below, when dialogue exists

    # Ensure assets directory exists
    if not os.path.exists("assets"):
        os.makedirs("assets")

    # Helper to save metadata
    def save_metadata(outfile, mode, model_synth, voice_main, voice_sidebar, prompt_system, prompt_main, prompt_sidebar, dialogue, seed=None, temperature=None, status=None, usage=None, duration=None):
        
        # If remote, we must have already uploaded the file and 'outfile' is a URL
        # If local, 'outfile' is a path
        
        api_provider = os.environ.get("TTS_PROVIDER", "vertexai")
        
        # Process dialogue to include original and actual (phonetic) text
        processed_dialogue = []
        from gemini_url_to_audio import apply_pronunciation_dictionary, load_pronunciation_dictionary
        p_dict = load_pronunciation_dictionary() if apply_dictionary else {}
        
        for d in dialogue:
            new_d = d.copy()
            original_text = d.get("text", "")
            actual_text = apply_pronunciation_dictionary(original_text, p_dict) if apply_dictionary else original_text
            new_d["original_text"] = original_text
            new_d["text"] = actual_text
            processed_dialogue.append(new_d)
            
        # Estimate token usage if 0 (e.g. for CloudTTS)
        if usage and usage.get("total_token_count", 0) == 0:
            estimated_tokens = sum(len(d["text"]) // 4 for d in processed_dialogue)
            usage = {
                "prompt_token_count": estimated_tokens,
                "candidates_token_count": 0,
                "total_token_count": estimated_tokens
            }
        
        meta = {
            "timestamp": int(time.time()),
            "mode": mode,
            "url": url,
            "extraction_method": extraction_method,
            "model_parse": model_parse,
            "api_provider": api_provider,
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
            "duration_seconds": round(duration, 2) if duration else None,
            "dialogue": processed_dialogue,
            "full_text": st.session_state.text_content,
            "seed": seed,
            "temperature": temperature,
            "status": status,
            "usage": usage
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
            "prompt_tts_sidebar": prompt_sidebar,
            "seed": seed,
            "temperature": temperature,
            "status": status,
            "usage": usage
        })
        return outfile # Return the ref

    if "dialogue" in st.session_state:
        st.markdown("---")
        st.subheader("4. Génération")
        
        with st.expander("Paramètres de Prompt TTS", expanded=False):
            prompt_main = st.text_area("Prompt Speaker 1 (Principal)", key="pg_p_main", height=100)
            prompt_sidebar = st.text_area("Prompt Speaker 2 (Secondaire)", key="pg_p_sidebar", height=100)
            
            c_seed, c_temp, c_delay = st.columns(3)
            seed = c_seed.number_input("Seed (Optionnel)", value=42, min_value=0, step=1, help="Fixez une graine pour une génération déterministe.")
            temperature = c_temp.slider("Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1, help="0.0 = Plus déterministe, 1.0 = Plus créatif")
            delay_seconds = c_delay.slider("Délai entre segments (sec)", min_value=0.0, max_value=5.0, value=1.0, step=0.5, help="Ajoute un silence entre chaque segment audio.")
        
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
                
                display_text = block["text"]
                if show_phonetic:
                    from gemini_url_to_audio import apply_pronunciation_dictionary
                    display_text = apply_pronunciation_dictionary(display_text)
                
                # Use a separate variable for the text area return value to avoid overwriting block["text"] when previewing
                new_text = st.text_area(f"Texte {i+1}", value=display_text, height=100, key=f"gen_txt_{i}", label_visibility="collapsed", disabled=show_phonetic)
                if not show_phonetic:
                    block["text"] = new_text
                else:
                    st.caption("⚠️ Mode Aperçu Phonétique : Édition désactivée.")
        
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
                    
                    start_time = time.time()
                    outfile, status, usage = synthesize_multi_speaker(
                        single_dialogue, 
                        model=model_synth, 
                        voice_main=voice_main, 
                        voice_sidebar=voice_main,
                        output_file=outfile_name,
                        strict_mode=strict_mode,
                        prompt_main=prompt_main,
                        prompt_sidebar=prompt_sidebar,
                        seed=seed,
                        temperature=temperature,
                        apply_dictionary=apply_dictionary,
                        language=language
                    )
                    duration = time.time() - start_time
                    update_token_usage(usage)
                    if outfile:
                        if status and status.get("state") == "truncated":
                            st.warning(f"⚠️ Génération tronquée : {status.get('details')}")
                        
                        final_ref = outfile
                        if st.session_state.app_mode == "remote":
                            with open(outfile, "rb") as f:
                                final_ref = st.session_state.storage.save_file(f.read(), outfile)
                        
                        save_metadata(final_ref, "Single Voice (Voix Unique)", model_synth, voice_main, voice_main, system_prompt, prompt_main, prompt_sidebar, single_dialogue, seed, temperature, status, usage, duration)
                        
                        # Play LOCAL file (outfile) for immediate feedback, ensuring no GCS latency/auth issues
                        st.audio(outfile)
                        st.success(f"Sauvegardé : {final_ref}")
                        
        with c2:
            if st.button("Générer Double Voix"):
                with st.spinner("Synthèse Double Voix..."):
                     # Generate unique filename
                     timestamp = int(time.time())
                     outfile_name = f"assets/dual_{timestamp}.wav"
    
                     start_time = time.time()
                     outfile, status, usage = synthesize_multi_speaker(
                        st.session_state.dialogue, 
                        model=model_synth, 
                        voice_main=voice_main, 
                        voice_sidebar=voice_sidebar,
                        output_file=outfile_name,
                        strict_mode=strict_mode,
                        prompt_main=prompt_main,
                        prompt_sidebar=prompt_sidebar,
                        seed=seed,
                        temperature=temperature,
                        apply_dictionary=apply_dictionary,
                        delay_seconds=delay_seconds,
                        language=language
                    )
                     duration = time.time() - start_time
                     update_token_usage(usage)
                     if outfile:
                        if status and status.get("state") == "truncated":
                            st.warning(f"⚠️ Génération tronquée : {status.get('details')}")

                        final_ref = outfile
                        if st.session_state.app_mode == "remote":
                            with open(outfile, "rb") as f:
                                final_ref = st.session_state.storage.save_file(f.read(), outfile)

                        save_metadata(final_ref, "Dual Voice (Double Voix)", model_synth, voice_main, voice_sidebar, system_prompt, prompt_main, prompt_sidebar, st.session_state.dialogue, seed, temperature, status, usage, duration)
                        
                        # Play LOCAL file
                        st.audio(outfile)
                        st.success(f"Sauvegardé : {final_ref}")
    
        with c3:
            if st.button("Générer Comparaison (Standard)"):
                 with st.spinner("Synthèse Standard TTS..."):
                    try:
                        from gtts import gTTS
                        clean_text = " ".join(seg["text"] for seg in st.session_state.dialogue)
                        start_time = time.time()
                        tts = gTTS(text=clean_text, lang='fr')
                        timestamp = int(time.time())
                        outfile = f"assets/standard_{timestamp}.wav"
                        tts.save(outfile)
                        duration = time.time() - start_time
                        
                        final_ref = outfile
                        if st.session_state.app_mode == "remote":
                            with open(outfile, "rb") as f:
                                final_ref = st.session_state.storage.save_file(f.read(), outfile)

                        save_metadata(final_ref, "Standard Comparisons", "gTTS", "Standard", "Standard", system_prompt, "N/A", "N/A", st.session_state.dialogue, None, None, {"state": "completed", "details": "gTTS"}, {}, duration)
                        
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
                    
                    start_time = time.time()
                    outfile, status, usage = synthesize_multi_speaker(
                        first_segment, 
                        model=model_synth, 
                        voice_main=voice, 
                        voice_sidebar=voice, # comparison is single voice
                        output_file=outfile_name,
                        strict_mode=strict_mode,
                        prompt_main=prompt_main,
                        prompt_sidebar=prompt_sidebar,
                        seed=seed,
                        temperature=temperature,
                        apply_dictionary=apply_dictionary,
                        language=language
                    )
                    duration = time.time() - start_time
                    update_token_usage(usage)
                    
                    if outfile:
                        final_ref = outfile
                        if st.session_state.app_mode == "remote":
                            with open(outfile, "rb") as f:
                                final_ref = st.session_state.storage.save_file(f.read(), outfile)
                                
                        save_metadata(final_ref, "Benchmark", model_synth, voice, voice, system_prompt, prompt_main, prompt_sidebar, first_segment, seed, temperature, status, usage, duration)
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

def render_dictionary_test():
    st.header("🧪 Test & Validation du Dictionnaire")
    # Compact intro
    st.markdown("Validez les ajustements de prononciation (Cycle: Tester -> Écouter -> Valider).")

    # --- 1. Input Section ---
    col_input, col_opts = st.columns([3, 1])
    
    with col_input:
        if "test_text_val" not in st.session_state:
            st.session_state.test_text_val = "Shein"
        test_text = st.text_input("Texte à tester", key="test_text_val", help="Entrez un mot ou une phrase.")
    
    # Define callback for next word
    def next_word_callback():
        d = load_pronunciation_dictionary()
        if d:
            keys = list(d.keys())
            if keys:
                current_val = st.session_state.get("test_text_val", "Shein")
                try:
                    current_idx = keys.index(current_val)
                except ValueError:
                    current_idx = -1
                next_idx = (current_idx + 1) % len(keys)
                st.session_state.test_text_val = keys[next_idx]
                st.session_state.auto_run_next_word = True

    with col_opts:
        st.write("") 
        st.write("") 
        st.button("⏭️ Suivant", on_click=next_word_callback, use_container_width=True)

    from gemini_url_to_audio import apply_pronunciation_dictionary
    phonetic_preview = apply_pronunciation_dictionary(test_text)

    # --- 2. Generation Logic (Auto-load & Button) ---
    auto_run_test = False
    
    # Initialize prompt in session state if needed, for late-render access
    if "pg_p_main" not in st.session_state:
        st.session_state.pg_p_main = PROMPT_ANCHOR
    if "test_prompt_val" not in st.session_state:
        st.session_state.test_prompt_val = st.session_state.pg_p_main

    # Auto-load check
    if test_text:
        sanitized_text_chk = sanitize_text_for_filename(test_text)
        sanitized_preview_chk = sanitize_text_for_filename(phonetic_preview)
        
        raw_exists = os.path.exists(f"assets/dic_original_{sanitized_text_chk}.wav")
        corrected_exists = os.path.exists(f"assets/dic_adaptation_{sanitized_text_chk}_TO_{sanitized_preview_chk}.wav")
        
        # Trigger if files exist and we haven't loaded this specific text result yet
        if raw_exists and corrected_exists:
             if "last_test_result" not in st.session_state or st.session_state.last_test_result.get("text") != test_text:
                 auto_run_test = True
    
    # Auto-run from Next Word click
    if st.session_state.get("auto_run_next_word", False):
        auto_run_test = True
        st.session_state.auto_run_next_word = False

    # Generation Action
    if st.button("🎧 Générer et Comparer", type="primary", use_container_width=True) or auto_run_test:
        if not test_text:
            st.error("Entrez du texte.")
        else:
             with st.spinner("Génération..."):
                 timestamp = int(time.time())
                 sanitized_text = sanitize_text_for_filename(test_text)
                 sanitized_preview = sanitize_text_for_filename(phonetic_preview)
                 test_prompt = st.session_state.test_prompt_val 

                 # 1. Raw
                 file_raw_path = f"assets/dic_original_{sanitized_text}.wav"
                 if os.path.exists(file_raw_path):
                     file_raw = file_raw_path
                     status_raw = {"state": "cached"}
                 else:
                     file_raw, status_raw, usage_raw = synthesize_and_save(
                         test_text, 
                         model=model_synth, 
                         voice=voice_main, 
                         output_file=file_raw_path, 
                         apply_dictionary=False,
                         system_instruction=None,
                         language=language
                     )
                     update_token_usage(usage_raw)
                 
                 # 2. Corrected
                 file_corrected_path = f"assets/dic_adaptation_{sanitized_text}_TO_{sanitized_preview}.wav"
                 if os.path.exists(file_corrected_path):
                     file_corrected = file_corrected_path
                     status_corr = {"state": "cached"}
                 else:
                     file_corrected, status_corr, usage_corr = synthesize_and_save(
                         test_text, 
                         model=model_synth, 
                         voice=voice_main, 
                         output_file=file_corrected_path, 
                         apply_dictionary=True,
                         system_instruction=test_prompt,
                         language=language
                     )
                     update_token_usage(usage_corr)
                 
                 # Save result
                 if file_raw and file_corrected:
                     st.session_state.last_test_result = {
                         "raw": file_raw,
                         "corrected": file_corrected,
                         "text": test_text
                     }

    # --- 3. Results Display (Prioritized) ---
    if "last_test_result" in st.session_state and st.session_state.last_test_result.get("text") == test_text:
        res = st.session_state.last_test_result
        
        st.divider()
        c_raw, c_corr = st.columns(2)
        
        with c_raw:
            st.caption("🔴 Sans Dictionnaire")
            if os.path.exists(res["raw"]):
                 with open(res["raw"], "rb") as f:
                     st.audio(f.read(), format="audio/wav")
        
        with c_corr:
            st.caption("🟢 Avec Dictionnaire")
            if os.path.exists(res["corrected"]):
                 with open(res["corrected"], "rb") as f:
                     st.audio(f.read(), format="audio/wav")
        
        # Validation Actions - Inline with results
        cv1, cv2 = st.columns(2)
        with cv1:
             st.button("👍 Valider", use_container_width=True, key="val_ok", help="Marquer comme correct (Feedback visuel uniquement)")
        with cv2:
             if st.button("👎 Modifier", use_container_width=True, key="val_ko"):
                 st.session_state.show_edit_dict = True

    # --- 4. Details: Visual Diff & Editing ---
    if test_text:
        st.divider()
        c_diff, c_edit = st.columns(2)
        
        with c_diff:
            st.subheader("🔍 Analyse")
            st.text(f"Original: {test_text}")
            if test_text != phonetic_preview:
                st.markdown(f"**Adapté**: `{phonetic_preview}`")
                st.success("Adaptation active")
            else:
                st.caption("Aucune règle ne s'applique.")

        with c_edit:
            st.subheader("✏️ Édition")
            # Determine if we show the form
            force_edit = st.session_state.get("show_edit_dict", False)
            
            # Load current dict value
            d_current = load_pronunciation_dictionary()
            current_val = d_current.get(test_text, "")
            
            # Simple Expandable Edit Form
            with st.expander("Modifier la prononciation", expanded=force_edit):
                new_pron = st.text_input("Notation Phonétique", value=current_val, key=f"edit_{test_text}")
                
                if st.button("Sauvegarder", type="primary"):
                    d = load_pronunciation_dictionary()
                    if new_pron.strip():
                        d[test_text] = new_pron.strip()
                        save_pronunciation_dictionary(d)
                        st.success(f"Enregistré: {new_pron}")
                        st.session_state.show_edit_dict = False
                        st.rerun()
                    else:
                        if test_text in d:
                            del d[test_text]
                            save_pronunciation_dictionary(d)
                            st.warning("Entrée supprimée")
                            st.session_state.show_edit_dict = False
                            st.rerun()

    # --- 5. Advanced Settings ---
    with st.expander("⚙️ Paramètres Avancés (Prompt)", expanded=False):
        st.text_area("Prompt Système", key="test_prompt_val", height=100, help="Prompt utilisé pour le contexte de la phrase.")

def render_voice_cloning():
    st.header("🧬 Voice Cloning (Demo)")
    st.warning("⚠️ Feature in Early Access (EAP). Requires permit-listed project.")
    
    st.markdown(f"Cette démo utilise le modèle **{DEFAULT_MODEL_CLONING}** pour cloner une voix à partir d'un échantillon audio de référence.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Reference Audio")
        uploaded_file = st.file_uploader("Upload Reference Voice (WAV)", type=["wav"])
        
        if uploaded_file is not None:
            st.audio(uploaded_file, format='audio/wav')
            st.success(f"Loaded: {uploaded_file.name}")
            
    with col2:
        st.subheader("2. Text to Speak")
        # Allow overriding region for EAP
        eap_location = st.text_input("Region (EAP Model)", value="us-central1", help="Try us-central1, us-east4, or europe-west4 if available.")
        text_input = st.text_area("Texte à synthétiser", value="Bonjour, ceci est une démonstration de clonage de voix avec Gemini.", height=150)
        
        if st.button("Generate Cloned Voice", type="primary"):
            if uploaded_file is None:
                st.error("Please upload a reference audio file first.")
            elif not text_input:
                st.error("Please enter text to speak.")
            else:
                with st.spinner(f"Cloning voice in {eap_location}..."):
                    # Get bytes
                    uploaded_file.seek(0)
                    ref_bytes = uploaded_file.read()
                    
                    # Generate filename
                    timestamp = int(time.time())
                    outfile_name = f"assets/cloned_{timestamp}.wav"
                    
                    outfile, status, usage = synthesize_replicated_voice(
                        text=text_input, 
                        reference_audio_bytes=ref_bytes, 
                        project_id=project_id, 
                        location=eap_location, 
                        output_file=outfile_name,
                        apply_dictionary=apply_dictionary,
                        language=language
                    )
                    update_token_usage(usage)
                    
                    if outfile:
                        st.audio(outfile)
                        st.success(f"Generated: {outfile}")
                        
                        # Save to history/storage if needed (Optional for demo)
                        if st.session_state.app_mode == "remote":
                             try:
                                with open(outfile, "rb") as f:
                                    final_ref = st.session_state.storage.save_file(f.read(), outfile)
                                    st.info(f"Saved to Remote: {final_ref}")
                             except Exception as e:
                                 st.error(f"Remote save failed: {e}")

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
                
                # Check status
                status = item.get("status", {})
                if status and status.get("state") == "truncated":
                    c4.write(f"⚠️ {date_str}")
                else:
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
                             logging.warning(f"Could not download audio (likely 404): {e}")
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
        
        c_seed_pg, c_temp_pg = st.columns(2)
        seed_pg = c_seed_pg.number_input("Seed", value=42, min_value=0, step=1, key="pg_seed")
        temperature_pg = c_temp_pg.slider("Temperature", min_value=0.0, max_value=2.0, value=0.0, step=0.1, key="pg_temp")

    if st.button("Générer l'audio du script", key="pg_generate", type="primary", use_container_width=True):
        if not st.session_state.playground_dialogue:
            st.error("Le script est vide.")
        else:
             with st.spinner("Synthèse du script en cours..."):
                timestamp = int(time.time())
                outfile_name = f"assets/playground_script_{timestamp}.wav"
                
                dialogue_to_synth = st.session_state.playground_dialogue
                
                outfile, status, usage = synthesize_multi_speaker(
                    dialogue_to_synth, 
                    model=model_synth, 
                    voice_main=voice_main, 
                    voice_sidebar=voice_sidebar,
                    output_file=outfile_name,
                    strict_mode=strict_mode,
                    prompt_main=prompt_main,
                    prompt_sidebar=PROMPT_REPORTER,
                    seed=seed_pg,
                    temperature=temperature_pg,
                    apply_dictionary=apply_dictionary,
                    language=language
                )
                update_token_usage(usage)
                
                if outfile:
                    if status and status.get("state") == "truncated":
                        st.warning(f"⚠️ Génération tronquée : {status.get('details')}")
                    final_ref = outfile
                    if st.session_state.app_mode == "remote":
                         with open(outfile, "rb") as f:
                                final_ref = st.session_state.storage.save_file(f.read(), outfile)

                    # Process dialogue to include original and actual (phonetic) text
                    processed_dialogue = []
                    from gemini_url_to_audio import apply_pronunciation_dictionary, load_pronunciation_dictionary
                    p_dict = load_pronunciation_dictionary() if apply_dictionary_pg else {}
                    
                    for d in dialogue_to_synth:
                        new_d = d.copy()
                        original_text = d.get("text", "")
                        actual_text = apply_pronunciation_dictionary(original_text, p_dict) if apply_dictionary_pg else original_text
                        new_d["original_text"] = original_text
                        new_d["text"] = actual_text
                        processed_dialogue.append(new_d)
                        
                    # Estimate token usage if 0 (e.g. for CloudTTS)
                    if usage and usage.get("total_token_count", 0) == 0:
                        estimated_tokens = sum(len(d["text"]) // 4 for d in processed_dialogue)
                        usage = {
                            "prompt_token_count": estimated_tokens,
                            "candidates_token_count": 0,
                            "total_token_count": estimated_tokens
                        }

                    # Save metadata
                    meta = {
                        "timestamp": int(time.time()),
                        "mode": "Playground Script",
                        "url": "Playground Input",
                        "extraction_method": "Script Builder",
                        "model_parse": "N/A",
                        "api_provider": os.environ.get("TTS_PROVIDER", "vertexai"),
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
                        "duration_seconds": round(duration, 2) if 'duration' in locals() else None,
                        "dialogue": processed_dialogue,
                        "full_text": " [Script] ",
                        "seed": seed_pg,
                        "temperature": temperature_pg,
                        "status": status,
                        "usage": usage
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

if "Générateur" in nav:
    render_generator()
elif "Test Dictionnaire" in nav:
    render_dictionary_test()
elif "Voice Cloning" in nav:
    render_voice_cloning()
else:
    render_history()
