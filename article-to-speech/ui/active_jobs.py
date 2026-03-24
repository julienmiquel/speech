import streamlit as st
import time
from job_manager import manager as job_manager
from async_helpers import async_dual_voice, async_single_voice
from workflows.generation import enqueue_automation_followup

@st.fragment(run_every="2s")
def display_active_jobs():
    """Renders progress bars for active jobs and handles completion state."""
    if "active_jobs" not in st.session_state:
        st.session_state.active_jobs = {}
        
    jobs_to_clear = []
    
    for job_id, job_info in list(st.session_state.active_jobs.items()):
        job = job_manager.get_job(job_id)
        if not job: continue
        status = job['status']
        job_type = job_info['type']
        
        if status == "running":
            st.progress(job.get('progress', 0.0), text=f"⏳ {job_type}: {job.get('message', '')} ({int(job.get('progress',0)*100)}%)")
        elif status == "completed":
            st.success(f"✅ {job_type} completé ! {job.get('message', '')}")
            res = job['result']
            
            if job_type == "Automatisation":
                if res.get("text_content"): st.session_state.text_content = res["text_content"]
                if res.get("pronunciation_guides"): st.session_state.pronunciation_guides = res["pronunciation_guides"]
                if res.get("dialogue"): st.session_state.dialogue = res["dialogue"]
                if res.get("truncated"): st.warning("Le résultat a été tronqué !")
                
                u = res.get("total_usage")
                if "token_usage" in st.session_state and u:
                    st.session_state.token_usage["prompt"] += u.get("prompt_token_count", 0)
                    st.session_state.token_usage["candidates"] += u.get("candidates_token_count", 0)
                    st.session_state.token_usage["total"] += u.get("total_token_count", 0)
                
                queued = enqueue_automation_followup(res, job_info, job_manager)
                if queued:
                    new_job_id, new_job_info = queued
                    st.session_state.active_jobs[new_job_id] = new_job_info
                    
                jobs_to_clear.append(job_id)
                st.rerun()
                
            elif job_type in ["Double Voix", "Voix Unique"]:
                u = res.get("usage")
                if "token_usage" in st.session_state and u:
                    st.session_state.token_usage["prompt"] += u.get("prompt_token_count", 0)
                    st.session_state.token_usage["candidates"] += u.get("candidates_token_count", 0)
                    st.session_state.token_usage["total"] += u.get("total_token_count", 0)
                    
                # FastAPI already saves metadata!
                outfile = res.get("audio_url", res.get("outfile"))
                
                if outfile:
                    st.audio(outfile)
                    
            jobs_to_clear.append(job_id)
            
        elif status == "error":
            st.error(f"❌ {job_type} a échoué: {job.get('error')}")
            if st.button(f"Fermer l'erreur", key=f"close_{job_id}"):
                jobs_to_clear.append(job_id)
            
    for j in jobs_to_clear:
        if j in st.session_state.active_jobs:
            del st.session_state.active_jobs[j]
        
    if jobs_to_clear:
        st.rerun()
