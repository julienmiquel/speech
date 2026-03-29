import os
import time
import requests
import logging

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def _poll_api_job(updater, api_job_id):
    """Internal helper to poll a job from the FastAPI backend."""
    while True:
        try:
            r = requests.get(f"{API_BASE_URL}/jobs/{api_job_id}")
            if r.status_code == 200:
                data = r.json()
                status = data.get("status")
                if status == "running":
                    updater(data.get("progress", 0), data.get("message", "Processing on server..."))
                elif status == "completed":
                    updater(1.0, data.get("message", "Completed!"))
                    return data.get("result", {})
                elif status == "error":
                    raise Exception(data.get("error", "Unknown API error"))
            elif r.status_code == 404:
                raise Exception("Job vanished from API.")
        except Exception as e:
            logging.error(f"Error polling API job: {e}")
            # Do not exit immediately on network error, but sleep and loop
        time.sleep(1)

def async_automation(updater, manual_text_input, text_content, source_option, url, extraction_method, model_parse, language, strict_mode, preset_system_prompt, opt_manual, opt_url, opt_rss):
    """
    Submits an automation request to the backend and polls it.
    """
    updater(0.05, "Sending automation request to backend...")
    
    # Send the URL to the backend. Note: manual_text_input isn't supported purely yet in automate endpoint 
    # but the automate endpoint expects a URL. For manual text we skip fetching anyway.
    req = {
        "url": url if source_option in [opt_url, opt_rss] else "manual",
        "method": "gemini" if "gemini" in (extraction_method or "").lower() else "bs4",
        "model_parse": model_parse,
        "language": language,
        "strict_mode": strict_mode,
        "preset_system_prompt": preset_system_prompt
    }
    
    # For fully manual text, we'll just bypass automation and return it straight to the UI
    if source_option == opt_manual:
         return {
            "text_content": manual_text_input, "pronunciation_guides": None, "dialogue": None, "added_dict": 0,
            "total_usage": {}, "truncated": False
         }
         
    try:
        r = requests.post(f"{API_BASE_URL}/automate/async", json=req)
        r.raise_for_status()
        job_id = r.json()["job_id"]
        return _poll_api_job(updater, job_id)
    except Exception as e:
        raise Exception(f"Failed to submit automation to API: {e}")

def async_dual_voice(updater, dialogue, model_synth, voice_main, voice_sidebar, strict_mode, prompt_main, prompt_sidebar, seed, temperature, apply_dictionary, delay_seconds, language, outfile_name):
    updater(0.05, "Sending multi-speaker synthesis request to backend...")
    req = {
        "text": "",
        "is_multi_speaker": True,
        "dialogue_segments": dialogue,
        "voice_main": voice_main,
        "voice_sidebar": voice_sidebar,
        "strict_mode": strict_mode,
        "prompt_main": prompt_main,
        "prompt_sidebar": prompt_sidebar,
        "seed": seed,
        "temperature": temperature,
        "apply_dictionary": apply_dictionary,
        "delay_seconds": delay_seconds,
        "language": language,
        "output_filename": outfile_name,
        "model_synth": model_synth
    }
    try:
        r = requests.post(f"{API_BASE_URL}/synthesize/async", json=req)
        r.raise_for_status()
        job_id = r.json()["job_id"]
        res = _poll_api_job(updater, job_id)
        return {"outfile": res.get("audio_url"), "status": res.get("status"), "usage": res.get("usage"), "duration": 0}
    except Exception as e:
        raise Exception(f"Synthesis failed: {e}")

def async_single_voice(updater, dialogue, model_synth, voice_main, apply_dictionary, prompt_main, language, outfile_name):
    updater(0.05, "Sending single-speaker synthesis request to backend...")
    req = {
        "text": "\n\n".join([d["text"] for d in dialogue]),
        "is_multi_speaker": False,
        "voice_main": voice_main,
        "strict_mode": False,
        "prompt_main": prompt_main,
        "apply_dictionary": apply_dictionary,
        "language": language,
        "output_filename": outfile_name,
        "model_synth": model_synth
    }
    try:
        r = requests.post(f"{API_BASE_URL}/synthesize/async", json=req)
        r.raise_for_status()
        job_id = r.json()["job_id"]
        res = _poll_api_job(updater, job_id)
        return {"outfile": res.get("audio_url"), "status": res.get("status"), "usage": res.get("usage"), "duration": 0}
    except Exception as e:
        raise Exception(f"Synthesis failed: {e}")
