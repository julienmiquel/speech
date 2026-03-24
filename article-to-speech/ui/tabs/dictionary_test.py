import streamlit as st
import time
import os
from api import (
    load_pronunciation_dictionary,
    save_pronunciation_dictionary,
    apply_pronunciation_dictionary,
    synthesize_and_save
)
# removed app import
import re

def sanitize_for_filename(text):
    text = text.replace("é", "e").replace("è", "e").replace("à", "a").replace("ç", "c")
    return re.sub(r'[^a-zA-Z0-9]', '_', text).strip('_')

def render_dictionary_test_tab(model_synth, voice_main, language):
    st.header("🧪 Test & Validation du Dictionnaire")
    st.markdown("Validez les ajustements de prononciation (Cycle: Tester -> Écouter -> Valider).")

    col_input, col_opts = st.columns([3, 1])
    
    with col_input:
        if "test_text_val" not in st.session_state:
            st.session_state.test_text_val = "Shein"
        test_text = st.text_input("Texte à tester", key="test_text_val", help="Entrez un mot ou une phrase.")
    
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

    phonetic_preview = apply_pronunciation_dictionary(test_text)
    auto_run_test = False
    
    if "pg_p_main" not in st.session_state:
        st.session_state.pg_p_main = ""
    if "test_prompt_val" not in st.session_state:
        st.session_state.test_prompt_val = st.session_state.pg_p_main

    if test_text:
        sanitized_text_chk = sanitize_for_filename(test_text)
        sanitized_preview_chk = sanitize_for_filename(phonetic_preview)
        
        raw_exists = os.path.exists(f"assets/dic_original_{sanitized_text_chk}.wav")
        corrected_exists = os.path.exists(f"assets/dic_adaptation_{sanitized_text_chk}_TO_{sanitized_preview_chk}.wav")
        
        if raw_exists and corrected_exists:
             if "last_test_result" not in st.session_state or st.session_state.last_test_result.get("text") != test_text:
                 auto_run_test = True
    
    if st.session_state.get("auto_run_next_word", False):
        auto_run_test = True
        st.session_state.auto_run_next_word = False

    if st.button("🎧 Générer et Comparer", type="primary", use_container_width=True) or auto_run_test:
        if not test_text:
            st.error("Entrez du texte.")
        else:
             with st.spinner("Génération..."):
                 timestamp = int(time.time())
                 sanitized_text = sanitize_for_filename(test_text)
                 sanitized_preview = sanitize_for_filename(phonetic_preview)
                 test_prompt = st.session_state.test_prompt_val 

                 file_raw_path = f"assets/dic_original_{sanitized_text}.wav"
                 
                 def update_token_usage_local(u):
                    if hasattr(st.session_state, "token_usage") and u:
                        st.session_state.token_usage["prompt"] += u.get("prompt_token_count", 0)
                        st.session_state.token_usage["candidates"] += u.get("candidates_token_count", 0)
                        st.session_state.token_usage["total"] += u.get("total_token_count", 0)

                 if os.path.exists(file_raw_path):
                     file_raw = file_raw_path
                 else:
                     file_raw, _, usage_raw = synthesize_and_save(
                         test_text, model=model_synth, voice=voice_main, output_file=file_raw_path, 
                         apply_dictionary=False, system_instruction=None, language=language
                     )
                     update_token_usage_local(usage_raw)
                 
                 file_corrected_path = f"assets/dic_adaptation_{sanitized_text}_TO_{sanitized_preview}.wav"
                 if os.path.exists(file_corrected_path):
                     file_corrected = file_corrected_path
                 else:
                     file_corrected, _, usage_corr = synthesize_and_save(
                         test_text, model=model_synth, voice=voice_main, output_file=file_corrected_path, 
                         apply_dictionary=True, system_instruction=test_prompt, language=language
                     )
                     update_token_usage_local(usage_corr)
                 
                 if file_raw and file_corrected:
                     st.session_state.last_test_result = {
                         "raw": file_raw,
                         "corrected": file_corrected,
                         "text": test_text
                     }

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
        
        cv1, cv2 = st.columns(2)
        with cv1:
             st.button("👍 Valider", use_container_width=True, key="val_ok")
        with cv2:
             if st.button("👎 Modifier", use_container_width=True, key="val_ko"):
                 st.session_state.show_edit_dict = True

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
            force_edit = st.session_state.get("show_edit_dict", False)
            d_current = load_pronunciation_dictionary()
            current_val = d_current.get(test_text, "")
            
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

    with st.expander("⚙️ Paramètres Avancés (Prompt)", expanded=False):
        st.text_area("Prompt Système", key="test_prompt_val", height=100)
