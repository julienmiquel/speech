import urllib
import os
import hashlib
import logging
import re
from api.config import CACHE_DIR

def hash_url(url):
    """Returns an MD5 hash of the URL."""
    return hashlib.md5(url.encode()).hexdigest()

def get_cached_text(url):
    """Retrieves cached text for a URL if it exists."""
    cache_file = os.path.join(CACHE_DIR, f"{hash_url(url)}.txt")
    if os.path.exists(cache_file):
        logging.info(f"Loading text from cache for URL: {url}")
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()
    return None

def save_to_cache(url, text):
    """Saves extracted text to local cache."""
    if not text:
        return
    cache_file = os.path.join(CACHE_DIR, f"{hash_url(url)}.txt")
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(text)
    logging.info(f"Saved text to cache for URL: {url}")

def convert_url_to_file_name(url):
    """Converts a URL into a safe filename string."""
    clean_url = re.sub(r'^https?://', '', url)
    clean_url = re.sub(r'^www\.', '', clean_url)
    return re.sub(r'[^a-zA-Z0-9]', '_', clean_url).strip('_')

def split_text_into_chunks(text, max_len=3500):
    """Splits a single large text into smaller chunks."""
    chunks = []
    while len(text) > max_len:
        split_idx = text.rfind('.', 0, max_len)
        if split_idx == -1: split_idx = text.rfind(' ', 0, max_len)
        if split_idx == -1: split_idx = max_len
        chunks.append(text[:split_idx+1].strip())
        text = text[split_idx+1:].strip()
    if text: 
        chunks.append(text)
    return chunks

import time
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
    if dialogue:
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

