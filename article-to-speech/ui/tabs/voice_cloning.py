import streamlit as st
import time
import os
import requests
from async_helpers import _poll_api_job, API_BASE_URL

def render_voice_cloning_tab(project_id, apply_dictionary, language):
    st.header("🧬 Voice Cloning (Demo)")
    st.warning("⚠️ Feature in Early Access (EAP). Requires permit-listed project.")
    
    DEFAULT_MODEL_CLONING = "gemini-2.5-flash"  # Extracted from constants
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
        eap_location = st.text_input("Region (EAP Model)", value="us-central1", help="Try us-central1, us-east4, or europe-west4 if available.")
        text_input = st.text_area("Texte à synthétiser", value="Bonjour, ceci est une démonstration de clonage de voix avec Gemini.", height=150)
        
        if st.button("Generate Cloned Voice", type="primary"):
            if uploaded_file is None:
                st.error("Please upload a reference audio file first.")
            elif not text_input:
                st.error("Please enter text to speak.")
            else:
                with st.spinner(f"Cloning voice in {eap_location}..."):
                    uploaded_file.seek(0)
                    ref_bytes = uploaded_file.read()
                    
                    timestamp = int(time.time())
                    outfile_name = f"assets/cloned_{timestamp}.wav"
                    
                    def update_token_usage_local(u):
                        if hasattr(st.session_state, "token_usage") and u:
                            st.session_state.token_usage["prompt"] += u.get("prompt_token_count", 0)
                            st.session_state.token_usage["candidates"] += u.get("candidates_token_count", 0)
                            st.session_state.token_usage["total"] += u.get("total_token_count", 0)

                    def clone_voice_via_api():
                        files = {
                            "reference_audio": (uploaded_file.name, ref_bytes, "audio/wav")
                        }
                        data = {
                            "text": text_input,
                            "project_id": project_id,
                            "location": eap_location,
                            "apply_dictionary": str(apply_dictionary).lower(),
                            "language": language,
                            "output_filename": f"cloned_{timestamp}.wav"
                        }
                        
                        r = requests.post(f"{API_BASE_URL}/synthesize/clone/async", files=files, data=data)
                        r.raise_for_status()
                        job_id = r.json()["job_id"]
                        
                        # Use a local dummy updater just to display current spinner status natively
                        def local_updater(prog, msg):
                             pass
                             
                        return _poll_api_job(local_updater, job_id)
                        
                    try:
                        res = clone_voice_via_api()
                        outfile = res.get("audio_url")
                        usage = res.get("usage")
                        update_token_usage_local(usage)
                    except Exception as e:
                        st.error(f"Erreur de clonage API: {e}")
                        outfile = None
                    
                    if outfile:
                        st.audio(outfile)
                        st.success(f"Generated: {outfile}")
                        
                        if st.session_state.get("app_mode") == "remote":
                             try:
                                with open(outfile, "rb") as f:
                                    final_ref = st.session_state.storage.save_file(f.read(), outfile)
                                    st.info(f"Saved to Remote: {final_ref}")
                             except Exception as e:
                                 st.error(f"Remote save failed: {e}")
