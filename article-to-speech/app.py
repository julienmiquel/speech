import streamlit as st
import os
import time

# --- Setup & Locales ---
from ui.locales import init_locales, _t
init_locales()

st.set_page_config(page_title="Gemini TTS Workshop", layout="wide")

# --- Globals & Core Dependencies ---
from api import (
    DEFAULT_MODEL_PARSE, DEFAULT_MODEL_SYNTH, DEFAULT_VOICE_MAIN, DEFAULT_VOICE_SIDEBAR
)
from storage import LocalStorage, RemoteStorage
from dotenv import load_dotenv

load_dotenv()

# --- Initialize Storage & App Mode ---
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
        
    if "storage_v2" not in st.session_state:
        st.session_state.storage_v2 = RemoteStorage(bucket_name, project_id)
else:
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "customer-demo-01")
    if "storage_v2" not in st.session_state:
        st.session_state.storage_v2 = LocalStorage()

if "storage_v2" in st.session_state:
    st.session_state.storage = st.session_state.storage_v2

location = os.getenv("LOCATION", "europe-west9")
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

# Ensure assets dir
if not os.path.exists("assets"):
    os.makedirs("assets")

# Initialize Token Usage
if "token_usage" not in st.session_state:
    st.session_state.token_usage = {"prompt": 0, "candidates": 0, "total": 0}

# --- Shared UI Components ---
from ui.sidebar import render_sidebar
render_sidebar()

st.title(_t("app_title"))
st.markdown(_t("app_subtitle"))

# --- Configuration Expander ---
with st.expander("⚙️ Paramètres Audios & Modèles", expanded=False):
    cfg_col1, cfg_col2 = st.columns(2)

    with cfg_col1:
        st.subheader(_t("sidebar_models"))
        
        parse_models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite-preview", "gemini-3-flash-preview"]
        try: idx_parse = parse_models.index(DEFAULT_MODEL_PARSE)
        except ValueError: idx_parse = 0
        model_parse = st.selectbox(_t("parse_model"), parse_models, index=idx_parse)
        
        synth_models = ["gemini-2.5-pro-tts", "gemini-2.5-flash-tts", "gemini-2.5-flash-lite-preview-tts"]
        try: idx_synth = synth_models.index(DEFAULT_MODEL_SYNTH)
        except ValueError: idx_synth = 0
        model_synth = st.selectbox(_t("synth_model"), synth_models, index=idx_synth)
        
        st.subheader(_t("sidebar_language"))
        languages = ["fr-FR", "en-US", "en-GB", "de-DE", "es-ES"]
        language = st.selectbox(_t("sidebar_language"), list(languages), index=0)

    with cfg_col2:
        st.subheader(_t("sidebar_voices"))
        voices_available = [
            "Achernar", "Achird", "Algenib", "Algieba", "Alnilam", 
            "Aoede", "Autonoe", "Callirrhoe", "Charon", "Despina", 
            "Encelade", "Erinome", "Fenrir", "Gacrux", "Iapetus", 
            "Kore", "Laomedeia", "Léda", "Orus", "Pulcherrima", 
            "Puck", "Rasalgethi", "Sadachbia", "Sadaltager", "Schedar", 
            "Sulafat", "Umbriel", "Vindemiatrix", "Zephyr", "Zubenelgenubi"
        ]
        
        try: idx_main = voices_available.index(DEFAULT_VOICE_MAIN)
        except ValueError: idx_main = 0
        
        try: idx_side = voices_available.index(DEFAULT_VOICE_SIDEBAR)
        except ValueError: idx_side = 1
        
        voice_main = st.selectbox(_t("voice_main"), voices_available, index=idx_main)
        voice_sidebar = st.selectbox(_t("voice_sidebar"), voices_available, index=idx_side)

# --- Navigation Routing ---
st.markdown("---")
nav_options = {
    "🎙️ Générateur": _t("tab_generate"),
    "🧪 Test Dictionnaire": _t("tab_dict"),
    "🛝 Playground": "🛝 Playground",
    "🧬 Voice Cloning": "🧬 Voice Cloning",
    "🕵️ Review": "🕵️ Review",
    "📜 Historique": _t("tab_history")
}
nav = st.radio("Navigation", list(nav_options.keys()), horizontal=True, label_visibility="collapsed", format_func=lambda x: nav_options[x])
st.markdown("---")

# Import Views
from ui.active_jobs import display_active_jobs
from ui.extraction import render_extraction_section
from ui.generation import render_generation_section
from ui.tabs.dictionary_test import render_dictionary_test_tab
from ui.tabs.voice_cloning import render_voice_cloning_tab
from ui.tabs.history import render_history_tab
from ui.tabs.playground import render_playground_tab
from ui.tabs.review import render_review_tab

if "Générateur" in nav:
    display_active_jobs()
    
    source_option, url, extraction_method, strict_mode, system_prompt = render_extraction_section(model_parse)
    apply_dictionary = st.session_state.get("apply_dictionary", True)

    if st.session_state.get("run_automation"):
        st.session_state.run_automation = False
        from job_manager import manager as job_manager
        from async_helpers import async_automation
        
        info = {
            "mode": "Automation (Full Pipeline)",
            "url": url,
            "extraction_method": extraction_method,
            "model_parse": model_parse,
            "model_synth": model_synth,
            "voice_main": voice_main,
            "voice_sidebar": voice_sidebar,
            "strict_mode": strict_mode,
            "apply_dictionary": apply_dictionary,
            "prompts": {
                "system": system_prompt,
                "tts_main": st.session_state.get("pg_p_main", "Read main content"),
                "tts_sidebar": st.session_state.get("pg_p_sidebar", "Read sidebar content")
            },
            "seed": 42,
            "temperature": 1.0,
            "delay_seconds": 1.0,
            "language": language
        }
        
        job_id = job_manager.submit_job(
            async_automation,
            st.session_state.get("manual_text_input", ""),
            st.session_state.get("text_content", ""),
            source_option,
            url,
            extraction_method,
            model_parse,
            language,
            strict_mode,
            system_prompt,
            _t("opt_manual"), _t("opt_url"), _t("opt_rss")
        )
        
        if "active_jobs" not in st.session_state:
            st.session_state.active_jobs = {}
        st.session_state.active_jobs[job_id] = {"type": "Automatisation", "auto_generate": True, "meta": info}
        st.rerun()

    # Render generation section if we have content
    apply_dictionary = st.session_state.get("apply_dictionary", True)
    render_generation_section(
        url, extraction_method, model_parse, model_synth,
        voice_main, voice_sidebar, strict_mode,
        system_prompt, language, apply_dictionary
    )
elif "Test Dictionnaire" in nav:
    render_dictionary_test_tab(model_synth, voice_main, language)
elif "Playground" in nav:
    # Adding playground to top-level navigation instead of deeply nested in Generation
    apply_dictionary = st.session_state.get("apply_dictionary", True)
    render_playground_tab(model_synth, voice_main, voice_sidebar, apply_dictionary, language)
elif "Voice Cloning" in nav:
    apply_dictionary = st.session_state.get("apply_dictionary", True)
    render_voice_cloning_tab(project_id, apply_dictionary, language)
elif "Review" in nav:
    render_review_tab()
else:
    render_history_tab()
