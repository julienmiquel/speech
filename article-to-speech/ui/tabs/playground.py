import streamlit as st
import time
import os
import json
from job_manager import manager as job_manager
from async_helpers import async_dual_voice
from prompts import MODELS_CONFIG, PROMPT_ANCHOR, PROMPT_REPORTER

def render_playground_tab(model_synth, voice_main, voice_sidebar, apply_dictionary, language):
    st.subheader("🛝 Playground (Constructeur de Script)")
    st.markdown("Construisez votre script bloc par bloc ou chargez un fichier JSON.")
    
    # Define demo texts for different languages
    demo_texts = {
        "Français (FR)": [
            {"speaker": "R", "text": "Bonjour ! Nous sommes ravis de vous présenter nos capacités de synthèse vocale.", "prompt": ""},
            {"speaker": "S", "text": "Où vous pouvez diriger une voix, créer des dialogues réalistes, et bien plus encore.", "prompt": ""}
        ],
        "English (EN)": [
            {"speaker": "R", "text": "Hello! We are thrilled to introduce our text-to-speech synthesis capabilities.", "prompt": ""},
            {"speaker": "S", "text": "Where you can direct a voice, create realistic dialogue, and much more.", "prompt": ""}
        ],
        "Deutsch (DE)": [
            {"speaker": "R", "text": "Hallo! Wir freuen uns, Ihnen unsere Funktionen zur Sprachsynthese vorzustellen.", "prompt": ""},
            {"speaker": "S", "text": "Hier können Sie eine Stimme lenken, realistische Dialoge erstellen und vieles mehr.", "prompt": ""}
        ],
        "Español (ES)": [
            {"speaker": "R", "text": "¡Hola! Estamos encantados de presentar nuestras capacidades de síntesis de voz.", "prompt": ""},
            {"speaker": "S", "text": "Donde puedes dirigir una voz, crear diálogos realistas y mucho más.", "prompt": ""}
        ]
    }
    
    st.markdown("---")
    demo_lang = st.selectbox("Langue de démonstration", list(demo_texts.keys()), index=0)

    # Initialize session state for playground dialogue if not exists
    if "playground_dialogue" not in st.session_state:
        st.session_state.playground_dialogue = demo_texts[list(demo_texts.keys())[0]]
        st.session_state.demo_lang = list(demo_texts.keys())[0]

    if "demo_lang" not in st.session_state or st.session_state.demo_lang != demo_lang:
        st.session_state.demo_lang = demo_lang
        st.session_state.playground_dialogue = demo_texts[demo_lang]
        st.rerun()

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
        
        with st.expander("Instructions de Style (System Prompt)", expanded=False):
             system_prompt_pg = st.text_area("System Prompt", value="Read aloud in a warm, welcoming tone", height=70)
        
        dialogue = st.session_state.playground_dialogue
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
        
        if to_remove >= 0:
            dialogue.pop(to_remove)
            st.rerun()
            
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

    is_multi_speaker_supported = MODELS_CONFIG.get(model_synth, {}).get("multi_speaker", True)
    if not is_multi_speaker_supported:
        st.button("Générer l'audio du script (❌ Non supporté)", key="pg_generate_disabled", type="primary", use_container_width=True, disabled=True)
    elif st.button("Générer l'audio du script", key="pg_generate", type="primary", use_container_width=True):
        if not st.session_state.playground_dialogue:
            st.error("Le script est vide.")
        else:
             with st.spinner("Synthèse du script en cours..."):
                timestamp = int(time.time())
                outfile_name = f"assets/playground_script_{timestamp}.wav"
                
                dialogue_to_synth = st.session_state.playground_dialogue
                
                progress_bar_pg = st.progress(0, text="Préparation de la synthèse du script...")
                audio_container_pg = st.container()
                def update_progress_pg(pct, message=None):
                    progress_bar_pg.progress(pct, text=message or "Synthèse en cours...")
                        
                def update_token_usage_local(u):
                    if hasattr(st.session_state, "token_usage") and u:
                        st.session_state.token_usage["prompt"] += u.get("prompt_token_count", 0)
                        st.session_state.token_usage["candidates"] += u.get("candidates_token_count", 0)
                        st.session_state.token_usage["total"] += u.get("total_token_count", 0)
                    
                try:
                    res = async_dual_voice(
                        update_progress_pg,
                        dialogue=dialogue_to_synth, 
                        model_synth=model_synth, 
                        voice_main=voice_main, 
                        voice_sidebar=voice_sidebar,
                        strict_mode=strict_mode,
                        prompt_main=prompt_main,
                        prompt_sidebar=PROMPT_REPORTER,
                        seed=seed_pg,
                        temperature=temperature_pg,
                        apply_dictionary=apply_dictionary,
                        delay_seconds=0,
                        language=language,
                        outfile_name=outfile_name
                    )
                    outfile = res.get("outfile")
                    status = res.get("status")
                    usage = res.get("usage")
                except Exception as e:
                    st.error(f"Erreur de synthèse: {e}")
                    outfile = None
                    status = None
                    usage = None
                    
                progress_bar_pg.empty()
                update_token_usage_local(usage)
                
                if outfile:
                    if status and status.get("state") == "truncated":
                        st.warning(f"⚠️ Génération tronquée : {status.get('details')}")
                    final_ref = outfile
                    if st.session_state.get("app_mode") == "remote":
                         with open(outfile, "rb") as f:
                                final_ref = st.session_state.storage.save_file(f.read(), outfile)

                    processed_dialogue = []
                    for d in dialogue_to_synth:
                        new_d = d.copy()
                        original_text = d.get("text", "")
                        # Pronunciations are handled by the API backend
                        new_d["original_text"] = original_text
                        new_d["text"] = original_text
                        processed_dialogue.append(new_d)
                        
                    if usage and usage.get("total_token_count", 0) == 0:
                        estimated_tokens = sum(len(d["text"]) // 4 for d in processed_dialogue)
                        usage = {
                            "prompt_token_count": estimated_tokens,
                            "candidates_token_count": 0,
                            "total_token_count": estimated_tokens
                        }

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
                    
                    if "storage" in st.session_state:
                        st.session_state.storage.save_metadata(meta, final_ref)

                    local_playback_path = final_ref
                    if st.session_state.get("app_mode") == "remote":
                         if os.path.exists(outfile):
                             local_playback_path = outfile
                         else:
                             local_playback_path = "assets/temp_playback.wav"
                             st.session_state.storage.download_file(final_ref, local_playback_path)

                    st.audio(local_playback_path)
                    st.success(f"Généré et sauvegardé dans l'historique !")
