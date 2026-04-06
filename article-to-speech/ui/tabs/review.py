"""
Tab for reviewing actor performance.
"""
import streamlit as st
import os
from api.reviewer import review_recording

def render_review_tab():
    st.subheader("🕵️ Actor Performance Review")
    st.markdown("Upload a recording and provide the target prompt to get feedback.")

    uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3"])
    prompt_used = st.text_area("Target Style Prompt", height=100, placeholder="# AUDIO PROFILE: ...\n## THE SCENE: ...")

    if st.button("Review Performance", type="primary"):
        if not uploaded_file:
            st.error("Please upload an audio file.")
        elif not prompt_used.strip():
            st.error("Please enter the target prompt.")
        else:
            with st.spinner("Reviewing audio with Gemini..."):
                audio_bytes = uploaded_file.read()
                # Determine mime type
                mime_type = "audio/wav" if uploaded_file.name.endswith(".wav") else "audio/mpeg"
                
                feedback = review_recording(audio_bytes, prompt_used, mime_type=mime_type)
                
                st.markdown("### Review Results")
                st.markdown(feedback)
