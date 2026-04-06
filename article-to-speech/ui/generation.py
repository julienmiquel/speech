import streamlit as st
import time
import os
import logging
import requests
from ui.locales import _t

API_URL = os.getenv("API_URL", "http://localhost:8000")
from job_manager import manager as job_manager
from async_helpers import async_single_voice, async_dual_voice
from workflows.generation import build_metadata
from prompts import MODELS_CONFIG

def render_generation_section(
    url, extraction_method, model_parse, model_synth,
    voice_main, voice_sidebar, strict_mode,
    system_prompt, language, apply_dictionary
):
    """Renders the generation section containing Pronunciation Research, Structuring, and Audio Synthesis."""
    
    if "text_content" not in st.session_state or not st.session_state.text_content:
        return

    st.markdown("---")
    st.subheader("2. 🔍 Recherche de Prononciation")
    
    # Expose token usage updater helper
    def update_token_usage_local(u):
        if hasattr(st.session_state, "token_usage") and u:
            st.session_state.token_usage["prompt"] += u.get("prompt_token_count", 0)
            st.session_state.token_usage["candidates"] += u.get("candidates_token_count", 0)
            st.session_state.token_usage["total"] += u.get("total_token_count", 0)

    if st.button("Lancer la recherche (Google Search)"):
        with st.spinner("Recherche Google en cours..."):
            try:
                resp = requests.post(f"{API_URL}/research", json={
                    "text": st.session_state.text_content,
                    "model": model_parse,
                    "language": language
                })
                resp.raise_for_status()
                data = resp.json()
                guides = data.get("guides", [])
                usage = data.get("usage", {})
                update_token_usage_local(usage)
            except Exception as e:
                st.error(f"Erreur recherche: {e}")
                guides = []
            if guides:
                st.session_state.pronunciation_guides = guides
                try:
                    resp = requests.post(f"{API_URL}/dictionary/update", json=guides)
                    resp.raise_for_status()
                    added = resp.json().get("added_count", 0)
                    st.success(f"{len(guides)} guides de prononciation trouvés !")
                except Exception as e:
                    st.error(f"Erreur mise à jour dico: {e}")
                    added = 0
                if added > 0:
                    st.info(f"➕ {added} nouveaux termes ajoutés au dictionnaire global.")
            else:
                st.warning("Aucun guide spécifique trouvé ou erreur de recherche.")

    if "pronunciation_guides" in st.session_state and st.session_state.pronunciation_guides:
        with st.expander("Guides de prononciation trouvés", expanded=True):
            for g in st.session_state.pronunciation_guides:
                disp_text = f"- **{g['term']}** : "
                if 'inline' in g and g['inline']: disp_text += f"Inline: '{g['inline']}' "
                if 'ipa' in g and g['ipa']: disp_text += f"| IPA: '{g['ipa']}'"
                if 'guide' in g: disp_text += f"{g['guide']}"
                st.write(disp_text)
            
            if st.button("Appliquer comme consignes (Prompts)"):
                guides_text = "\nConsignes de prononciation :\n" + "\n".join([f"- {g['term']} se prononce '{g.get('inline', g.get('guide', g.get('ipa', '')))}'" for g in st.session_state.pronunciation_guides])
                st.session_state.pg_p_main += guides_text
                st.session_state.pg_p_sidebar += guides_text
                st.success("Guides ajoutés aux prompts de synthèse !")
                st.rerun()

    st.markdown("---")
    st.subheader("3. Structuration")
    show_phonetic = st.checkbox("🔍 Afficher les adaptations de prononciation (Aperçu audio)", value=False)
    
    if st.button("Analyser la Structure"):
            final_prompt = system_prompt
            if strict_mode:
                final_prompt += "\nCRITICAL: STRICT MODE ENABLED.\n- Do NOT change a single word of the original text.\n- Do NOT add any pauses, vocal tags, or extra punctuation.\n- Do NOT remove any text unless it is clearly navigation/menu/ad garbage.\n- The \"text\" field MUST match the original content EXACTLY word-for-word.\n"
            else:
                final_prompt += "\nIMPORTANT: To improve the reading flow, insert the following tags into the \"text\" content where appropriate:\n- [short pause] : Insert this tag between distinct list items or short clauses to create a natural breathing pause.\n- [medium pause] : Insert this tag between major sentences or distinct ideas.\n- [long pause] : Insert this tag before a significant topic change or dramatic statement.\nYou MAY also use the following \"Vocal Tags\" (didascalies) to match the emotion of the content:\n- [curious] : Use for questions or intriguing statements.\n- [surprised] : Use for shocking or unexpected information.\n- [laughing] : Use for lighter, humorous, or ironic content.\n- [whispering] : Use for sensitive information.\n- [sigh] : Use for discouraging or heavy news.\nCRITICAL: Ensure every \"text\" segment ends with a period (.) if it does not already end with a punctuation mark.\nDo NOT use these tags excessively, only where they improve the natural rhythm of a news reading.\n"

            try:
                resp = requests.post(f"{API_URL}/parse", json={
                    "text": st.session_state.text_content,
                    "model": model_parse,
                    "strict_mode": strict_mode,
                    "system_prompt": final_prompt
                })
                resp.raise_for_status()
                data = resp.json()
                dialogue = data.get("dialogue")
                usage = data.get("usage", {})
                is_truncated = data.get("is_truncated", False)
                update_token_usage_local(usage)
            except Exception as e:
                st.error(f"Erreur parsing: {e}")
                dialogue = None
                is_truncated = False
            
            if is_truncated:
                st.warning("⚠️ Le texte extrait est trop long (>500,000 caractères) et a été tronqué lors de l'analyse structurelle.")
            
            if dialogue:
                st.session_state.dialogue = dialogue
                st.success(f"Analysé {len(dialogue)} segments.")
            else:
                st.error("Échec de l'analyse structurelle.")

    if "dialogue" in st.session_state:
        st.markdown("---")
        st.subheader("4. Génération")
        
        with st.expander("Paramètres de Prompt TTS", expanded=False):
            from actor_prompts import ACTORS
            
            # Actor selection
            actor_names = ["-- Select Actor --"] + list(ACTORS.keys())
            selected_actor = st.selectbox("Virtual Voice Actor (Optional Override)", actor_names, key="actor_select")
            
            if selected_actor != "-- Select Actor --":
                actor_data = ACTORS[selected_actor]
                st.caption(f"**Profile:** {actor_data['profile']}")
                
                c1, c2 = st.columns(2)
                if c1.button("Apply to Speaker 1"):
                    st.session_state.pg_p_main = actor_data["prompt"]
                    st.rerun()
                if c2.button("Apply to Speaker 2"):
                    st.session_state.pg_p_sidebar = actor_data["prompt"]
                    st.rerun()
            
            tab_main, tab_sec = st.tabs(["Voix Principale", "Voix Secondaire"])
            with tab_main:
                prompt_main = st.text_area("Prompt Speaker 1 (Principal)", key="pg_p_main", height=100, label_visibility="collapsed")
            with tab_sec:
                prompt_sidebar = st.text_area("Prompt Speaker 2 (Secondaire)", key="pg_p_sidebar", height=100, label_visibility="collapsed")
            
            c_seed, c_temp, c_delay = st.columns(3)
            seed = c_seed.number_input("Seed (Optionnel)", value=42, min_value=0, step=1, help="Fixez une graine pour une génération déterministe.", key="tts_seed")
            temperature = c_temp.slider("Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1, help="0.0 = Plus déterministe, 1.0 = Plus créatif", key="tts_temperature")
            delay_seconds = c_delay.slider("Délai entre segments (sec)", min_value=0.0, max_value=5.0, value=1.0, step=0.5, help="Ajoute un silence entre chaque segment audio.", key="tts_delay")
        
        # Script Builder UI
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
                    try:
                        resp = requests.post(f"{API_URL}/apply_dictionary", json={"text": display_text})
                        resp.raise_for_status()
                        display_text = resp.json().get("text", display_text)
                    except Exception as e:
                        st.caption(f"⚠️ Erreur opti phonétique: {e}")
                
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
            if st.button("Générer Voix Unique", use_container_width=True):
                single_dialogue = [d.copy() for d in st.session_state.dialogue]
                for d in single_dialogue: d["speaker"] = "R"
                
                timestamp = int(time.time())
                ext = MODELS_CONFIG.get(model_synth, {}).get("default_format", "wav")
                outfile_name = f"assets/single_{timestamp}.{ext}"
                
                job_id = job_manager.submit_job(
                    async_single_voice,
                    single_dialogue, model_synth, voice_main, apply_dictionary, prompt_main, language, outfile_name
                )
                
                info = {
                    "mode": "Single Voice (Voix Unique)",
                    "url": url,
                    "extraction_method": extraction_method,
                    "model_parse": model_parse,
                    "model_synth": model_synth,
                    "voice_main": voice_main,
                    "voice_sidebar": voice_main,
                    "strict_mode": strict_mode,
                    "apply_dictionary": apply_dictionary,
                    "prompts": {
                        "system": system_prompt,
                        "tts_main": prompt_main,
                        "tts_sidebar": prompt_sidebar
                    },
                    "dialogue": single_dialogue,
                    "seed": seed,
                    "temperature": temperature,
                    "delay_seconds": delay_seconds,
                    "language": language
                }
                
                if "active_jobs" not in st.session_state:
                    st.session_state.active_jobs = {}
                st.session_state.active_jobs[job_id] = {"type": "Voix Unique", "meta": info}
                st.rerun()
                        
        with c2:
            st.write("") # spacer
            is_multi_speaker_supported = MODELS_CONFIG.get(model_synth, {}).get("multi_speaker", True)
            if not is_multi_speaker_supported:
                st.button("Générer Double Voix (❌ Non supporté)", disabled=True, use_container_width=True)
            elif st.button("Générer Double Voix", use_container_width=True):
                timestamp = int(time.time())
                ext = MODELS_CONFIG.get(model_synth, {}).get("default_format", "wav")
                outfile_name = f"assets/dual_{timestamp}.{ext}"
                
                job_id = job_manager.submit_job(
                    async_dual_voice,
                    st.session_state.dialogue, model_synth, voice_main, voice_sidebar, strict_mode, prompt_main, prompt_sidebar, seed, temperature, apply_dictionary, delay_seconds, language, outfile_name
                )
                
                info = {
                    "mode": "Dual Voice (Double Voix)",
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
                        "tts_main": prompt_main,
                        "tts_sidebar": prompt_sidebar
                    },
                    "dialogue": st.session_state.dialogue,
                    "seed": seed,
                    "temperature": temperature,
                    "delay_seconds": delay_seconds,
                    "language": language
                }
                if "active_jobs" not in st.session_state:
                    st.session_state.active_jobs = {}
                st.session_state.active_jobs[job_id] = {"type": "Double Voix", "meta": info}
                st.rerun()
    
        with c3:
            if st.button("Générer Comparaison (Standard)", use_container_width=True):
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
                        if st.session_state.get("app_mode") == "remote":
                            with open(outfile, "rb") as f:
                                final_ref = st.session_state.storage.save_file(f.read(), outfile)

                        meta = build_metadata(
                            final_ref, "Standard Comparisons", url, extraction_method,
                            model_parse, "gTTS", "Standard", "Standard", strict_mode,
                            system_prompt, "N/A", "N/A", st.session_state.dialogue,
                            None, None, apply_dictionary, {"state": "completed", "details": "gTTS"},
                            {}, duration, st.session_state.text_content
                        )
                        st.session_state.storage.save_metadata(meta, final_ref)
                        if "history" not in st.session_state: st.session_state.history = []
                        
                        st.session_state.history.append({
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "mode": "Standard Comparisons",
                            "model": "gTTS",
                            "url": url,
                            "voices": "Standard / Standard",
                            "audio_file": final_ref,
                            "prompt_system": system_prompt,
                            "prompt_tts_main": "N/A",
                            "prompt_tts_sidebar": "N/A",
                            "seed": None,
                            "temperature": None,
                            "status": {"state": "completed"},
                            "usage": {}
                        })
                        
                        st.audio(outfile)
                        st.success(f"Sauvegardé : {final_ref}")
                    except ImportError:
                        st.error("gTTS non installé.")
