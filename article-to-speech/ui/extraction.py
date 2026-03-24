import streamlit as st
import logging
from ui.locales import _t
from workflows.extraction import fetch_rss_feed, perform_extraction
from prompts import PROMPT_ANCHOR, PROMPT_REPORTER, SYSTEM_PROMPT_STANDARD, SYSTEM_PROMPT_NEWS_SMART

# Make sure this function caches RSS feed per session
@st.cache_data(ttl=300)
def cached_fetch_lemonde_rss():
    return fetch_rss_feed(
        fallback_no_title=_t("rss_no_title"),
        fallback_no_desc=_t("rss_no_desc")
    )

def render_extraction_section(model_parse):
    """Renders the extraction section and returns the context needed for generation."""
    
    st.subheader(_t("tab_extract"))
    source_option = st.radio(_t("input_method"), [_t("opt_manual"), _t("opt_url"), _t("opt_rss")], index=0, horizontal=True)

    # Initialize variables to avoid NameError
    strict_mode = True
    system_prompt = SYSTEM_PROMPT_STANDARD

    # Automation Button at the top for convenience
    url = ""
    extraction_method = _t("opt_manual")

    if st.button(_t("btn_automation"), use_container_width=True):
        st.session_state.run_automation = True

    if source_option == _t("opt_rss"):
        st.subheader(_t("rss_header"))
        st.caption(f"{_t('rss_source_link')} [https://www.lemonde.fr/rss/en_continu.xml](https://www.lemonde.fr/rss/en_continu.xml)")
        
        rss_items = cached_fetch_lemonde_rss()
        if not rss_items:
            st.error(_t("rss_error"))
            url = ""
            extraction_method = _t("opt_manual")
        else:
            options_dict = {f"{i+1}. {item['title']}": item['link'] for i, item in enumerate(rss_items)}
            selected_title = st.selectbox(_t("rss_select"), list(options_dict.keys()))
            url = options_dict[selected_title]
            
            # Show description preview
            idx = int(selected_title.split(".")[0]) - 1
            st.caption(f"**{_t('rss_summary')}** {rss_items[idx]['description']}")
            st.info(f"{_t('rss_url_info')} {url}")
            
            if "last_url" not in st.session_state:
                st.session_state.last_url = url
            if url != st.session_state.last_url:
                st.session_state.last_url = url
                st.session_state.text_content = ""
                if "dialogue" in st.session_state:
                    del st.session_state.dialogue

            st.subheader(_t("btn_extract"))
            extraction_method = st.radio("Méthode d'extraction", [f"{model_parse} (Smart)", "BeautifulSoup (Standard)"], index=0, horizontal=True)

    elif source_option == _t("opt_url"):
        # Presets
        presets = {
            "Custom URL": "",
            "Long Article (Quotes + Enrichments)": "https://www.lefigaro.fr/politique/j-ai-pris-la-decision-d-etre-candidat-de-la-place-beauvau-a-la-conquete-de-l-elysee-la-mue-presidentielle-de-bruno-retailleau-20260212",
            "Editorial": "https://www.lefigaro.fr/vox/economie/l-editorial-de-gaetan-de-capele-strategie-energetique-il-faut-sanctuariser-le-nucleaire-20260211",
            "Economy (Figures)": "https://www.lefigaro.fr/conjoncture/l-industrie-automobile-francaise-a-perdu-un-tiers-de-ses-effectifs-entre-2010-et-2023-constate-l-insee-20260212",
            "Interview (Q&A)": "https://www.lefigaro.fr/musique/lord-kossity-le-rap-c-est-un-art-et-la-jeune-generation-fait-tout-sauf-du-rap-20260211",
            "International (Foreign Names)": "https://www.lefigaro.fr/international/le-pentagone-prepare-le-deploiement-d-un-deuxieme-porte-avions-pour-accroitre-la-pression-sur-l-iran-selon-le-wall-street-journal-20260212",
            "Brands (Shein)": "https://www.lefigaro.fr/conso/les-plateformes-d-ultra-fast-fashion-seduisent-toujours-plus-d-un-francais-sur-trois-en-2025-d-apres-une-etude-20260212"
        }

        if "last_preset" not in st.session_state:
            st.session_state.last_preset = "Custom URL"

        selected_preset = st.selectbox("Load Example Article", list(presets.keys()))

        if "url_input" not in st.session_state:
            st.session_state.url_input = "https://www.lefigaro.fr/meteo/meteo-decouvrez-les-16-departements-places-en-vigilance-orange-crues-ou-pluie-inondation-ce-11-fevrier-20260210"

        if selected_preset != st.session_state.last_preset:
            st.session_state.last_preset = selected_preset
            if selected_preset != "Custom URL":
                 st.session_state.url_input = presets[selected_preset]
                 st.rerun()

        url = st.text_input(_t("url_input"), key="url_input")
        
        if "last_url" not in st.session_state:
            st.session_state.last_url = url
            
        if url != st.session_state.last_url:
            logging.info(f"URL changed from '{st.session_state.last_url}' to '{url}'. Clearing extraction/analysis state.")
            st.session_state.last_url = url
            st.session_state.text_content = ""
            if "dialogue" in st.session_state:
                del st.session_state.dialogue

        st.subheader(_t("btn_extract"))
        extraction_method = st.radio("Méthode d'extraction", [f"{model_parse} (Smart)", "BeautifulSoup (Standard)"], index=0, horizontal=True)
    else:
        url = _t("opt_manual")
        extraction_method = _t("opt_manual")
        
        if "manual_text_input" not in st.session_state:
            st.session_state.manual_text_input = ""
            
        st.subheader("Saisissez votre texte")
        st.text_area(_t("opt_manual"), height=200, key="manual_text_input")
        
        if st.button("Valider le texte"):
            if st.session_state.manual_text_input.strip() != st.session_state.get("text_content", "").strip():
                st.session_state.text_content = st.session_state.manual_text_input
                if "dialogue" in st.session_state:
                    del st.session_state.dialogue
            st.success(f"Texte validé ({len(st.session_state.text_content)} caractères).")

    system_prompts = {
        "Standard": SYSTEM_PROMPT_STANDARD,
        "News Smart (Rich Content)": SYSTEM_PROMPT_NEWS_SMART
    }
    
    if "text_content" not in st.session_state:
        st.session_state.text_content = ""

    if "pg_p_main" not in st.session_state:
        st.session_state.pg_p_main = PROMPT_ANCHOR
    if "pg_p_sidebar" not in st.session_state:
        st.session_state.pg_p_sidebar = PROMPT_REPORTER

    # Tips Section based on Feedback
    with st.expander("💡 Tips & Guide (Feedbacks)", expanded=False):
        st.markdown("""
        **Bonnes Pratiques :**
        - **Prononciation** : Les prompts incluent des guides pour "Fillon", "Retailleau", etc. Vous pouvez aussi ajouter des précisions phonétiques entre parenthèses dans le texte (ex: "80 (quatre-vingts)").
        - **Didascalies** : Utilisez des balises comme `[short pause]`, `[long pause]`, `[surprised]`, `[laughing]` directement dans le texte pour plus d'expressivité.
        - **Contenus Enrichis** : Utilisez le prompt "News Smart" pour mieux gérer les descriptions d'images/vidéos.
        - **Voix** : "Speaker 1" = Voix Principale, "Speaker 2" = Voix Encarts (ex: Fenrir).
        """)

    with st.expander("Paramètres de Parsing", expanded=False):
        strict_mode = st.checkbox("Mode Strict (Aucun changement de mot)", value=True)

        system_prompt_choice = st.selectbox("System Prompt Template", list(system_prompts.keys()), index=0)
        default_system_prompt = system_prompts[system_prompt_choice]

        system_prompt = st.text_area("System Prompt (Parsing)", value=default_system_prompt, height=150)
        
    if source_option in [_t("opt_url"), _t("opt_rss")] and st.button(_t("btn_extract"), use_container_width=True):
        with st.spinner(f"{_t('msg_extracting')}..."):
            text, is_cached, usage, is_truncated, error_msg = perform_extraction(url, extraction_method, model_parse)
            
            def update_token_usage_local(u):
                if u:
                    st.session_state.token_usage["prompt"] += u.get("prompt_token_count", 0)
                    st.session_state.token_usage["candidates"] += u.get("candidates_token_count", 0)
                    st.session_state.token_usage["total"] += u.get("total_token_count", 0)

            if usage: update_token_usage_local(usage)
            
            if text:
                st.session_state.text_content = text
                if is_cached:
                    st.success(_t("extracted_text"))
                else:
                    if is_truncated:
                        st.warning("⚠️ L'article complet dépasse les limites d'extraction de ce modèle et a été tronqué.")
                    st.success(f"Extrait {len(text)} caractères.")
            elif error_msg:
                st.error(_t("msg_error"))
                
    return source_option, url, extraction_method, strict_mode, system_prompt
