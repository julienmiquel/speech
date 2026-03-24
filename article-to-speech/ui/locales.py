import os
import json
import streamlit as st

# Fix for when locales.py is inside the ui/ directory. We need the parent directory.
LOCALES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales.json")

def load_locales():
    if os.path.exists(LOCALES_PATH):
        with open(LOCALES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    print(f"Warning: locales file not found at {LOCALES_PATH}")
    return {}

# Load once when module is imported
all_locales = load_locales()

def init_locales():
    """Initializes UI language in session state if not set."""
    if "ui_lang" not in st.session_state:
         st.session_state.ui_lang = "fr"

def _t(key, **kwargs):
    """Translation helper."""
    translations = all_locales.get(key, {})
    # Fallback to key if translation is completely missing
    text = translations.get(st.session_state.get("ui_lang", "fr"), key)
    
    if kwargs and isinstance(text, str):
        try:
            return text.format(**kwargs)
        except KeyError:
            return text # fail gracefully
    return text
