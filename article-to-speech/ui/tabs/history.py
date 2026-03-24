import streamlit as st
import time
import os
from ui.locales import _t

def render_history_tab():
    st.header("📜 Persistent History")
    
    if st.session_state.get("app_mode") == "remote":
        st.info(f"Connected to Remote Storage (GCS: {os.getenv('GCS_BUCKET_NAME')}, Firestore: {os.getenv('FIRESTORE_COLLECTION', 'generations')})")
    else:
        st.info("Browsing Local Storage (assets/)")
    
    import requests
    from async_helpers import API_BASE_URL
    
    # 1. Load Data via API
    try:
        r = requests.get(f"{API_BASE_URL}/history")
        r.raise_for_status()
        history_items = r.json().get("history", [])
    except Exception as e:
        st.error(f"Error fetching history from API: {e}")
        return

    if not history_items:
        st.info("No history found in API. Generate some audio first!")
        return

    # Normalize Loop
    normalized_items = []
    for data in history_items:
        if isinstance(data, list):
             pass
        # Normalize missing fields
        if "url" not in data: data["url"] = "Unknown URL"
        if "timestamp" not in data: data["timestamp"] = 0
        normalized_items.append(data)
    
    history_items = normalized_items

    # 2. Group by URL
    grouped = {}
    for item in history_items:
        url = item["url"]
        
        # Special handling for Playground to group by text content
        if url == "Playground Input":
            text_preview = str(item.get("full_text", ""))[:50].replace("\n", " ")
            if len(str(item.get("full_text", ""))) > 50:
                text_preview += "..."
            url = f"Playground: {text_preview}"
            
        if url not in grouped:
            grouped[url] = []
        grouped[url].append(item)
    
    # 3. Sort Groups by latest timestamp
    group_sorting = []
    for url, items in grouped.items():
        items.sort(key=lambda x: x["timestamp"], reverse=True)
        latest = items[0]["timestamp"]
        group_sorting.append((url, latest))
    
    group_sorting.sort(key=lambda x: x[1], reverse=True)

    # 4. Render
    for url, _ in group_sorting:
        items = grouped[url]
        count = len(items)
        
        with st.expander(f"📄 {url} ({count} versions)"):
            c_mode, c_model, c_voices, c_date = st.columns([1, 1.5, 2, 1.5])
            c_mode.markdown("**Mode**")
            c_model.markdown("**Model**")
            c_voices.markdown("**Voices**")
            c_date.markdown("**Date**")
            st.markdown("---")
            
            for item in items:
                timestamp = item["timestamp"]
                date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                
                c1, c2, c3, c4 = st.columns([1, 1.5, 2, 1.5])
                c1.write(item.get("mode", "?"))
                c2.write(item.get("model_synth", "?"))
                c3.write(f"{item.get('voice_main', '?')} / {item.get('voice_sidebar', '?')}")
                
                status = item.get("status", {})
                if status and status.get("state") == "truncated":
                    c4.write(f"⚠️ {date_str}")
                else:
                    c4.write(date_str)
                
                audio_file = item.get("audio_file")
                local_path = audio_file
                if st.session_state.get("app_mode") == "remote":
                     filename = os.path.basename(audio_file)
                     local_path = os.path.join("assets", filename)
                     
                     if not os.path.exists(local_path):
                         try:
                            st.session_state.storage.download_file(audio_file, local_path)
                         except Exception as e:
                             st.warning(f"Could not download audio: {e}")
                             local_path = None
                
                if local_path and os.path.exists(local_path):
                    st.audio(local_path)
                elif audio_file:
                     # Attempt to play public/remote url
                     st.audio(audio_file)
                else:
                     st.warning("Audio missing")
                
                with st.expander("Show Details (Prompts & JSON)"):
                    prompts = item.get("prompts", {})
                    st.caption("System Prompt")
                    st.text(prompts.get("system", "N/A"))
                    
                    pc1, pc2 = st.columns(2)
                    with pc1:
                        st.caption("Main Prompt")
                        st.text(prompts.get("tts_main", "N/A"))
                    with pc2:
                        st.caption("Sidebar Prompt")
                        st.text(prompts.get("tts_sidebar", "N/A"))
                        
                    st.json(item.get("dialogue"))
                
                st.markdown("---")
