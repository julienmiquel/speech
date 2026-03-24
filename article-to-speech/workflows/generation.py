import time
import os
import logging
import requests
import json
from prompts import MODELS_CONFIG

API_BASE_URL = "http://127.0.0.1:8000"

def build_metadata(
    outfile, mode, url, extraction_method, model_parse, model_synth,
    voice_main, voice_sidebar, strict_mode,
    prompt_system, prompt_main, prompt_sidebar,
    dialogue, seed, temperature, apply_dict,
    status=None, usage=None, duration=None,
    full_text=""
):
    """
    Builds the metadata dictionary for a generated audio file.
    Does not depend on Streamlit.
    """
    api_provider = os.environ.get("TTS_PROVIDER", "vertexai")
    
    # Process dialogue to include original and actual (phonetic) text
    processed_dialogue = []
    for d in dialogue:
        new_d = d.copy()
        original_text = d.get("text", "")
        # Pronunciations are handled by the API internally in FastAPI synth logic
        new_d["original_text"] = original_text
        new_d["text"] = original_text
        processed_dialogue.append(new_d)
        
    # Estimate token usage if 0 (e.g. for CloudTTS)
    if usage and usage.get("total_token_count", 0) == 0:
        estimated_tokens = sum(len(d["text"]) // 4 for d in processed_dialogue)
        usage = {
            "prompt_token_count": estimated_tokens,
            "candidates_token_count": 0,
            "total_token_count": estimated_tokens
        }

    meta = {
        "timestamp": int(time.time()),
        "mode": mode,
        "url": url,
        "extraction_method": extraction_method,
        "model_parse": model_parse,
        "api_provider": api_provider,
        "model_synth": model_synth,
        "voice_main": voice_main,
        "voice_sidebar": voice_sidebar,
        "strict_mode": strict_mode,
        "prompts": {
            "system": prompt_system,
            "tts_main": prompt_main,
            "tts_sidebar": prompt_sidebar
        },
        "audio_file": outfile,
        "duration_seconds": round(duration, 2) if duration else None,
        "dialogue": processed_dialogue,
        "full_text": full_text,
        "seed": seed,
        "temperature": temperature,
        "status": status,
        "usage": usage
    }
    
    return meta

def enqueue_automation_followup(res, job_info, job_manager):
    """
    If automation was requested, calls the API to synthesize the dialogue.
    Since job_manager in Streamlit polls by ID, we'll launch a local job
    that polls the API job ID and reports back to the UI.
    """
    if not job_info.get("auto_generate") or not res.get("dialogue"):
        return None
        
    dialogue = res["dialogue"]
    meta = job_info.get("meta", {})
    
    m_synth = meta.get("model_synth")
    ext = MODELS_CONFIG.get(m_synth, {}).get("default_format", "wav")
    outfile_name = f"dual_{int(time.time())}.{ext}" if MODELS_CONFIG.get(m_synth, {}).get("multi_speaker", True) else f"single_{int(time.time())}.{ext}"
    is_multi = MODELS_CONFIG.get(m_synth, {}).get("multi_speaker", True)
    
    payload = {
        "text": "\n\n".join([d["text"] for d in dialogue]),
        "is_multi_speaker": is_multi,
        "dialogue_segments": dialogue if is_multi else None,
        "voice_main": meta.get("voice_main"),
        "voice_sidebar": meta.get("voice_sidebar"),
        "output_filename": outfile_name,
        "strict_mode": meta.get("strict_mode", False),
        "prompt_main": meta["prompts"].get("tts_main", ""),
        "prompt_sidebar": meta["prompts"].get("tts_sidebar", ""),
        "seed": meta.get("seed"),
        "temperature": meta.get("temperature"),
        "apply_dictionary": meta.get("apply_dictionary", True),
        "delay_seconds": meta.get("delay_seconds", 0),
        "language": meta.get("language", "fr-FR"),
        "model_synth": m_synth
    }
    
    r = requests.post(f"{API_BASE_URL}/synthesize/async", json=payload)
    r.raise_for_status()
    api_job_id = r.json()["job_id"]
    
    # We create a local job_manager task that just polls the API until completion
    def poll_api_job(updater):
        while True:
            try:
                status_res = requests.get(f"{API_BASE_URL}/jobs/{api_job_id}")
                if status_res.status_code == 200:
                    data = status_res.json()
                    status = data.get("status")
                    if status == "running":
                        updater(progress=data.get("progress", 0), message=data.get("message", "Synthesizing on API..."))
                    elif status == "completed":
                        return data.get("result", {})
                    elif status == "error":
                        raise Exception(data.get("error", "Unknown API error"))
            except Exception as e:
                import logging
                logging.error(f"Error polling API job: {e}")
                # We do not fail immediately on network blips, just wait and retry
            time.sleep(2)

    new_job_id = job_manager.submit_job(poll_api_job)
    return new_job_id, {"type": "Double Voix" if is_multi else "Voix Unique", "meta": meta, "api_job_id": api_job_id}
