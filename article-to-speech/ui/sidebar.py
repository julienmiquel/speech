import streamlit as st
from ui.locales import _t
from ui.dictionary import render_dictionary_panel

def render_sidebar():
    """Renders the left sidebar configuration."""
    st.sidebar.header("Interface")
    st.sidebar.markdown("v1.0.1")
    
    # UI Language Selector
    st.session_state.ui_lang = st.sidebar.selectbox(
        "Language / Langue", 
        options=["fr", "en"], 
        format_func=lambda x: "Français" if x == "fr" else "English",
        index=0 if st.session_state.get("ui_lang", "fr") == "fr" else 1,
        key="ui_lang_selector"
    )

    st.sidebar.header(_t("sidebar_config"))

    # Display Remote/Local mode set in app.py
    if st.session_state.get("app_mode") == "remote":
        project_id = st.session_state.get("google_cloud_project", "unknown")
        st.sidebar.success(f"Remote Mode: {project_id}")

    # Token Usage Display
    st.sidebar.subheader(_t("cost_usage"))
    if "token_usage" in st.session_state:
        u = st.session_state.token_usage
        st.sidebar.caption(f"Prompt: {u.get('prompt', 0)} | Candidates: {u.get('candidates', 0)}")
        st.sidebar.info(f"**{_t('total_tokens')}: {u.get('total', 0)}**")

    # Dictionary Management Panel
    render_dictionary_panel()
