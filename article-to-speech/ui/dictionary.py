import streamlit as st
import json
import requests
import os
from ui.locales import _t

API_URL = os.getenv("API_URL", "http://localhost:8000")

def render_dictionary_panel():
    """Renders the Pronunciation Dictionary management panel (usually in the sidebar)."""
    st.sidebar.subheader(_t("pronunciation_dict"))
    st.session_state.apply_dictionary = st.sidebar.checkbox(
        _t("enable_dict"), 
        value=st.session_state.get("apply_dictionary", True), 
        help=_t("dict_help")
    )

    with st.sidebar.expander(f"📖 {_t('pronunciation_dict')}"):
        try:
            resp = requests.get(f"{API_URL}/dictionary")
            resp.raise_for_status()
            pronunciation_dict = resp.json()
        except Exception as e:
            st.error(f"Erreur chargement dico: {e}")
            pronunciation_dict = {}

        # 1. Individual Entry Editor
        st.subheader(_t("add_entry"))
        new_word = st.text_input(_t("original_word"), key="new_word_dict", placeholder="Shein")
        new_pron_inline = st.text_input(_t("pron_inline"), key="new_pron_inline_dict", placeholder="Chi-ine")
        new_pron_ipa = st.text_input(_t("pron_ipa"), key="new_pron_ipa_dict", placeholder="ʃi.in")

        if st.button(_t("btn_add"), use_container_width=True):
            if new_word and (new_pron_inline or new_pron_ipa):
                pronunciation_dict[new_word] = {
                    "inline": new_pron_inline,
                    "ipa": new_pron_ipa
                }
                try:
                    resp = requests.put(f"{API_URL}/dictionary", json=pronunciation_dict)
                    resp.raise_for_status()
                    st.success(f"{_t('msg_added')}: {new_word}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur sauvegarde: {e}")
            else:
                st.error(_t("msg_fill_words"))

        st.markdown("---")

        # 2. Bulk JSON Editor
        st.subheader(_t("json_editor"))
        dict_json = json.dumps(pronunciation_dict, indent=4, ensure_ascii=False)
        new_dict_json = st.text_area(_t("full_json"), value=dict_json, height=200)

        if st.button(_t("btn_save_json"), use_container_width=True):
            try:
                updated_dict = json.loads(new_dict_json)
                try:
                    resp = requests.put(f"{API_URL}/dictionary", json=updated_dict)
                    resp.raise_for_status()
                    st.success(_t("msg_dict_updated"))
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur sauvegarde: {e}")
            except Exception as e:
                st.error(f"{_t('msg_json_error')} : {e}")

        st.markdown("---")

        # 3. List and delete
        st.subheader(_t("current_entries"))
        for word, pron in list(pronunciation_dict.items()):
            col_text, col_del = st.columns([4, 1])

            if isinstance(pron, dict):
                disp = f"{word} → Inline: '{pron.get('inline','')}' | IPA: '{pron.get('ipa','')}'"
            else:
                disp = f"{word} → {pron} ({_t('old_format')})"

            col_text.text(disp)
            if col_del.button("🗑️", key=f"del_dict_{word}"):
                del pronunciation_dict[word]
                try:
                    resp = requests.put(f"{API_URL}/dictionary", json=pronunciation_dict)
                    resp.raise_for_status()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur suppression: {e}")
