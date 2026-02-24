import sys
import os
import requests
import re
from abc import ABC, abstractmethod
from google.cloud import texttospeech
from google import genai
from google.genai import types
import json
import wave
import logging
import base64
import hashlib
import time
from dotenv import load_dotenv
from prompts import (
    PROMPT_ANCHOR, PROMPT_REPORTER, EXTRACT_CONTENT_PROMPT, 
    RESEARCH_PRONUNCIATION_PROMPT, PARSING_INSTRUCTIONS_ENRICHED, 
    PARSING_INSTRUCTIONS_STRICT, SYSTEM_PROMPT_STANDARD
)

# Load environment variables from .env
load_dotenv()

# Path for pronunciation dictionary
DICTIONARY_PATH = os.path.join(os.path.dirname(__file__), "pronunciation_dictionary.json")

def load_pronunciation_dictionary():
    """Loads the pronunciation dictionary from a JSON file."""
    if os.path.exists(DICTIONARY_PATH):
        try:
            with open(DICTIONARY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading dictionary: {e}")
    return {}

def save_pronunciation_dictionary(dictionary):
    """Saves the pronunciation dictionary to a JSON file."""
    try:
        with open(DICTIONARY_PATH, "w", encoding="utf-8") as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logging.error(f"Error saving dictionary: {e}")
        return False

def update_pronunciation_dictionary(new_guides):
    """
    Updates the dictionary with new guides if they don't exist.
    new_guides: list of dicts [{"term": "...", "inline": "...", "ipa": "..."}]
    """
    if not new_guides:
        return 0
        
    current_dict = load_pronunciation_dictionary()
    added_count = 0
    for guide in new_guides:
        term = guide.get("term")
        inline = guide.get("inline", "")
        ipa = guide.get("ipa", "")
        
        # We also want to support the old "guide" format if the prompt occasionally falls back to it
        if not inline and not ipa and "guide" in guide:
            import re
            old_guide = guide["guide"]
            if re.search(r'[A-Z\-]', old_guide):
                inline = old_guide
            else:
                ipa = old_guide

        # Add only if we have at least one valid pronunciation
        if term and (inline or ipa) and term not in current_dict:
            current_dict[term] = {
                "inline": inline,
                "ipa": ipa
            }
            added_count += 1
            
    if added_count > 0:
        save_pronunciation_dictionary(current_dict)
    return added_count

def apply_pronunciation_dictionary(text, dictionary=None):
    """Replaces words in the text based on the 'inline' pronunciation dictionary field."""
    if dictionary is None:
        dictionary = load_pronunciation_dictionary()
    
    if not dictionary:
        return text
    
    # Sort keys by length descending to avoid partial replacements (e.g., 'Fillon' before 'Fill')
    sorted_keys = sorted(dictionary.keys(), key=len, reverse=True)
    
    processed_text = text
    for word in sorted_keys:
        entry = dictionary[word]
        # Handle new format (dict) or old legacy format (string fallback just in case)
        if isinstance(entry, dict):
            inline_val = entry.get("inline", "")
        else:
            inline_val = entry

        if inline_val: # Only replace if there is an inline pronunciation
            # Use regex for word boundaries to avoid replacing parts of other words
            pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
            processed_text = pattern.sub(inline_val, processed_text)
        
    return processed_text

def prepare_tts_dictionaries(p_dict, provider_type="cloudtts"):
    """
    Processes the raw pronunciation dictionary into formats suitable for TTS providers.
    - pseudo_dict: dict of {phrase: inline_replacement} for text-level replacement.
    - custom_pronunciations: (Cloud TTS only) list of CustomPronunciationParams.
    
    For Cloud TTS: IPA takes precedence. If a phrase has IPA, it is NOT added to pseudo_dict.
    For Vertex AI: Only inline replacements (pseudo_dict) are supported.
    """
    pseudo_dict = {}
    ipa_params = []
    applied_ipa = {}
    
    if not p_dict:
        return {}, [], {}

    unique_phrases = set()
    for k, v in p_dict.items():
        key_lower = k.lower()
        if key_lower not in unique_phrases:
            unique_phrases.add(key_lower)
            
            # Handle new dict format vs legacy string
            if isinstance(v, dict):
                inline_val = v.get("inline", "")
                ipa_val = v.get("ipa", "")
            else:
                # Legacy fallback
                if re.search(r'[A-Z\-]', v):
                    inline_val = v
                    ipa_val = ""
                else:
                    inline_val = ""
                    ipa_val = v
            
            if provider_type == "cloudtts" and ipa_val:
                # If Cloud TTS and IPA exists, we use IPA and skip inline replacement
                applied_ipa[k] = ipa_val
                ipa_params.append(
                    texttospeech.CustomPronunciationParams(
                        phrase=k,
                        pronunciation=ipa_val,
                        phonetic_encoding=texttospeech.CustomPronunciationParams.PhoneticEncoding.PHONETIC_ENCODING_IPA
                    )
                )
            elif inline_val:
                # Use inline replacement if no IPA (or if provider doesn't support it)
                pseudo_dict[k] = inline_val
                
    return pseudo_dict, ipa_params, applied_ipa

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Authenticate (Colab specific, kept for compatibility if run in Colab environment)
if "google.colab" in sys.modules:
    from google.colab import auth
    auth.authenticate_user()

# Configure Project and Client
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "customer-demo-01") 
LOCATION = os.getenv("LOCATION", "us-central1")

# Models & Voices (Defaults)
DEFAULT_MODEL_PARSE = os.getenv("MODEL_PARSE", "gemini-2.5-flash")
DEFAULT_MODEL_SYNTH = os.getenv("MODEL_SYNTH", "gemini-2.5-pro-tts")
DEFAULT_MODEL_CLONING = os.getenv("MODEL_CLONING", "gemini-2.5-flash-tts-eap-11-2025")
DEFAULT_VOICE_MAIN = os.getenv("VOICE_MAIN", "Aoede")
DEFAULT_VOICE_SIDEBAR = os.getenv("VOICE_SIDEBAR", "Fenrir")

# Initialize Vertex AI Client
try:
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    logging.info(f"Initialized Vertex AI client for project: {PROJECT_ID}, location: {LOCATION}")
except Exception as e:
    logging.error(f"Failed to initialize client: {e}")
    client = None

# Prompt Defaults imported from prompts.py

CACHE_DIR = "assets/cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

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

def extract_text_from_url(url):
    """
    Extracts text content from a given URL.
    Attempts to use BeautifulSoup if available, otherwise falls back to regex.
    """
    logging.info(f"Fetching URL (Standard): {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL: {e}")
        return None

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        logging.info(f"Standard extraction successful. Length: {len(text)}")
        return text
    except ImportError:
        logging.warning("BeautifulSoup not found. Using simple regex fallback.")
        # Regex fallback
        clean = re.sub(r'<(script|style).*?>.*?</\1>', '', html_content, flags=re.DOTALL)
        clean = re.sub(r'<.*?>', '', clean)
        clean = clean.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def _generate_content_with_retry(model, contents, config=None):
    """Internal helper to call Gemini with retry logic."""
    if config:
        return client.models.generate_content(model=model, contents=contents, config=config)
    else:
        return client.models.generate_content(model=model, contents=contents)

def extract_text_from_url_with_gemini(url, parsing_model=None):
    """
    Extracts text content from a URL using Gemini 2.5 Flash.
    """
    if parsing_model is None:
        parsing_model = DEFAULT_MODEL_PARSE
    logging.info(f"Fetching URL (Gemini): {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None, {}, False
        
    if not client:
        logging.error("Vertex AI Client not initialized.")
        return None, {}, False

    try:
        prompt = EXTRACT_CONTENT_PROMPT
        
        # Pre-clean HTML to remove massive script/style blocks before sending to Gemini
        clean_html = re.sub(r'<(script|style).*?>.*?</\1>', '', html_content, flags=re.DOTALL)
        
        logging.info(f"HTML Content length (Cleaned): {len(clean_html)}")

        is_truncated = len(clean_html) > 500000
        
        response = _generate_content_with_retry(
            model=parsing_model,
            contents=[prompt, clean_html[:500000]],
            config=types.GenerateContentConfig(response_mime_type="text/plain")
        )
        
        logging.info(f"Gemini extraction successful. Length: {len(response.text.strip())}")
        
        usage = {
            "prompt_token_count": response.usage_metadata.prompt_token_count,
            "candidates_token_count": response.usage_metadata.candidates_token_count,
            "total_token_count": response.usage_metadata.total_token_count
        } if response.usage_metadata else {}
        
        return response.text.strip(), usage, is_truncated
    except Exception as e:
        logging.error(f"Error extracting with Gemini for URL {url}: {e}")
        return None, {}, False

def convert_url_to_file_name(url):
    """Converts a URL into a safe filename string."""
    # Remove protocol and replace non-alphanumeric characters with underscores
    clean_url = re.sub(r'^https?://', '', url)
    clean_url = re.sub(r'^www\.', '', clean_url)
    clean_url = re.sub(r'^lefigaro.fr\.', '', clean_url)
    return re.sub(r'[^a-zA-Z0-9]', '_', clean_url).strip('_')

def intelligent_chunk(text, max_length=4000):
    """
    Intelligently splits text that is too long, trying to break at paragraphs (\\n\\n), 
    then lines (\\n), then sentences (.), ensuring no chunk exceeds max_length.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    
    # Hierarchical splitting strategy
    def split_and_accumulate(current_text, delimiter):
        parts = current_text.split(delimiter)
        accumulated = []
        current_chunk = ""
        
        for part in parts:
            # If a single part with the delimiter is still too long, we can't keep it whole
            if len(part) > max_length:
                # Flush current
                if current_chunk:
                    accumulated.append(current_chunk.strip())
                    current_chunk = ""
                # We need to fall back to a tighter delimiter for this huge part
                accumulated.extend([p for p in [part] if p.strip()]) 
            else:
                candidate = current_chunk + (delimiter if current_chunk else "") + part
                if len(candidate) <= max_length:
                    current_chunk = candidate
                else:
                    if current_chunk:
                        accumulated.append(current_chunk.strip())
                    current_chunk = part
                    
        if current_chunk:
            accumulated.append(current_chunk.strip())
            
        return accumulated

    # 1. Try splitting by paragraph
    paragraph_chunks = split_and_accumulate(text, "\n\n")
    
    # 2. Refine any chunk that is STILL too long via line breaks
    line_chunks = []
    for pc in paragraph_chunks:
        if len(pc) > max_length:
            line_chunks.extend(split_and_accumulate(pc, "\n"))
        else:
            line_chunks.append(pc)
            
    # 3. Refine any chunk that is STILL too long via sentences
    final_chunks = []
    for lc in line_chunks:
        if len(lc) > max_length:
            # Simple sentence split (approximate)
            sentence_chunks = split_and_accumulate(lc.replace(". ", ".|~|"), "|~|")
            for sc in sentence_chunks:
                if len(sc) > max_length:
                    # Absolute worst case fallback: arbitrary hard split
                    for i in range(0, len(sc), max_length):
                        final_chunks.append(sc[i:i+max_length])
                else:
                    final_chunks.append(sc)
        else:
            final_chunks.append(lc)
            
    return [c for c in final_chunks if c.strip()]


def parse_text_structure(text, model=None, strict_mode=False, system_prompt=None):
    """
    Uses a Flash model to separate the main text from 'encarts' (sidebars/inserts).
    Returns a list of segments: [{"text": "...", "speaker": "A"}, {"text": "...", "speaker": "B"}]
    Speaker A = Main text, Speaker B = Encarts
    """
    if model is None:
        model = DEFAULT_MODEL_PARSE
    if not client:
        logging.error("Client not initialized.")
        return None
    
    # Truncate parsing context if HUGE, but usually we need full context. 
    # Flash has a large context window, so 100k chars should be fine.
    
    if system_prompt:
        prompt = system_prompt
    else:
        prompt = SYSTEM_PROMPT_STANDARD

        if not strict_mode:
            prompt += PARSING_INSTRUCTIONS_ENRICHED
        else:
            prompt += PARSING_INSTRUCTIONS_STRICT

    is_truncated = len(text) > 500000
    prompt += f"""
    Article Text (Truncated for analysis if necessary):
    {text[:500000]} 
    """
    
    try:
        response = _generate_content_with_retry(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        json_text = response.text
        # Clean up code blocks if model returns them
        if json_text.startswith("```json"):
            json_text = json_text[7:]
        if json_text.strip().endswith("```"):
            json_text = json_text.strip()[:-3]
            
        segments = json.loads(json_text)
        
        # Map to speakers and enforce intelligent chunking
        dialogue = []
        for seg in segments:
            speaker = "R" if seg.get("type") == "main" else "S" # R = Reader (Main), S = Sidebar
            seg_text = seg.get("text", "")
            
            # Intelligent chunking to ensure no segment > 4000 characters
            sub_segments = intelligent_chunk(seg_text, 4000)
            for sub_text in sub_segments:
                dialogue.append({"text": sub_text, "speaker": speaker})
        
        usage = {
            "prompt_token_count": response.usage_metadata.prompt_token_count,
            "candidates_token_count": response.usage_metadata.candidates_token_count,
            "total_token_count": response.usage_metadata.total_token_count
        } if response.usage_metadata else {}
            
        return dialogue, usage, is_truncated
    except Exception as e:
        logging.error(f"Error parsing text structure: {e}")
        return None, {}, False

def research_pronunciations(text, model=None, language="fr-FR"):
    """
    Uses Gemini with Google Search tool to verify pronunciation of names and brands.
    """
    if model is None:
        model = DEFAULT_MODEL_PARSE
    if not client:
        return None
        
    prompt = RESEARCH_PRONUNCIATION_PROMPT.format(text_snippet=text[:500000], language=language)
    
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )
        )
        
        text_response = response.text.strip()
        
        # Robust JSON extraction: look for [ ... ]
        json_match = re.search(r"(\[.*\])", text_response, re.DOTALL)
        if json_match:
            text_response = json_match.group(1)
        else:
            # Fallback to previous manual cleanup if regex fails
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
        
        usage = {
            "prompt_token_count": response.usage_metadata.prompt_token_count,
            "candidates_token_count": response.usage_metadata.candidates_token_count,
            "total_token_count": response.usage_metadata.total_token_count
        } if response.usage_metadata else {}
        
        return json.loads(text_response.strip()), usage
    except Exception as e:
        logging.error(f"Error researching pronunciations: {e}. Raw response: {response.text if 'response' in locals() else 'N/A'}")
        return None, {}

class TTSProvider(ABC):
    @abstractmethod
    def synthesize_multi_speaker(self, dialogue, model=None, voice_main=None, voice_sidebar=None, output_file="output_multi.wav", strict_mode=False, prompt_main=PROMPT_ANCHOR, prompt_sidebar=PROMPT_REPORTER, seed=None, temperature=None, apply_dictionary=True, delay_seconds=0, language="fr-FR", progress_callback=None):
        pass

    @abstractmethod
    def synthesize_and_save(self, text, model=None, voice=None, output_file="output.wav", apply_dictionary=True, system_instruction=None, language="fr-FR", progress_callback=None):
        pass

    @abstractmethod
    def synthesize_replicated_voice(self, text, reference_audio_bytes, project_id, location="us-central1", output_file="output_cloned.wav", apply_dictionary=True, language="fr-FR"):
        pass

class VertexTTSProvider(TTSProvider):
    def synthesize_multi_speaker(self, dialogue, model=None, voice_main=None, voice_sidebar=None, output_file="output_multi.wav", strict_mode=False, prompt_main=PROMPT_ANCHOR, prompt_sidebar=PROMPT_REPORTER, seed=None, temperature=None, apply_dictionary=True, delay_seconds=0, language="fr-FR", progress_callback=None):
        if model is None: model = DEFAULT_MODEL_SYNTH
        if voice_main is None: voice_main = DEFAULT_VOICE_MAIN
        if voice_sidebar is None: voice_sidebar = DEFAULT_VOICE_SIDEBAR
        
        if not client:
            return None, {"state": "error", "details": "Client not initialized"}, {}
            
        logging.info(f"Synthesizing multi-speaker audio with {len(dialogue)} segments...")
        
        pseudo_dict = {}
        if apply_dictionary:
            p_dict = load_pronunciation_dictionary()
            pseudo_dict, _, _ = prepare_tts_dictionaries(p_dict, provider_type="vertexai")
        
        combined_audio = b""
        generation_status = {"state": "completed", "details": "All segments finished normally"}
        
        combined_usage = {
            "prompt_token_count": 0,
            "candidates_token_count": 0,
            "total_token_count": 0
        }

        for i, seg in enumerate(dialogue):
            text = apply_pronunciation_dictionary(seg["text"], pseudo_dict) if apply_dictionary else seg["text"]
            speaker = seg["speaker"]
            voice = voice_main if speaker == "R" else voice_sidebar
            
            logging.info(f"Segment {i}: Speaker {speaker} ({voice}) - {len(text)} chars")
            if not text.strip():
                continue
                
            prompt_instruction = seg.get("prompt")
            if not prompt_instruction:
                 if speaker == "R": 
                     prompt_instruction = prompt_main
                 else: 
                     prompt_instruction = prompt_sidebar
            
            if strict_mode:
                prompt_instruction += " Read the text EXACTLY as written, word for word. Do not add or remove anything."
            logging.info(f"Generating segment {i} ({speaker}) with prompt: {prompt_instruction[:100]}...")

            try:
                config_params = {
                    "response_modalities": ["AUDIO"],
                    "speech_config": types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice
                            )
                        ),
                        language_code=language
                    )
                }
                
                if seed is not None:
                    config_params["seed"] = seed
                    
                if temperature is not None:
                    config_params["temperature"] = temperature

                response = _generate_content_with_retry(
                    model=model,
                    contents=f"{prompt_instruction} Text to read: {text}",
                    config=types.GenerateContentConfig(**config_params)
                )
                
                if response.usage_metadata:
                    combined_usage["prompt_token_count"] += response.usage_metadata.prompt_token_count
                    combined_usage["candidates_token_count"] += response.usage_metadata.candidates_token_count
                    combined_usage["total_token_count"] += response.usage_metadata.total_token_count
                
                if response.candidates:
                    candidate = response.candidates[0]
                    if candidate.finish_reason != "STOP":
                        generation_status["state"] = "truncated"
                        generation_status["details"] = f"Segment {i} truncated. Reason: {candidate.finish_reason}"
                        logging.warning(f"Segment {i} truncated: {candidate.finish_reason}")
                    
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.inline_data:
                                import io
                                with wave.open(io.BytesIO(part.inline_data.data), 'rb') as w:
                                    combined_audio += w.readframes(w.getnframes())
                    
                    if delay_seconds > 0 and i < len(dialogue) - 1:
                        silence_bytes = b'\x00' * int(delay_seconds * 48000)
                        combined_audio += silence_bytes
                        logging.info(f"Added {delay_seconds}s of silence after segment {i}")
            except Exception as e:
                logging.error(f"Error generating audio for segment {i}: {e}")
                generation_status["state"] = "error"
                generation_status["details"] = str(e)
                
        if combined_audio:
             with wave.open(output_file, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(combined_audio)
             logging.info(f"Multi-speaker audio saved to {output_file}")
             return output_file, generation_status, combined_usage
             
        return None, generation_status, combined_usage

    def synthesize_and_save(self, text, model=None, voice=None, output_file="output.wav", apply_dictionary=True, system_instruction=None, language="fr-FR", progress_callback=None):
        if model is None: model = DEFAULT_MODEL_SYNTH
        if voice is None: voice = DEFAULT_VOICE_MAIN
        
        if not client:
            logging.error("Client not initialized.")
            return None, {"state": "error", "details": "Client not initialized"}, {}
            
        if apply_dictionary:
            p_dict = load_pronunciation_dictionary()
            pseudo_dict, _, _ = prepare_tts_dictionaries(p_dict, provider_type="vertexai")
            text = apply_pronunciation_dictionary(text, pseudo_dict)
        
        text_chunks = split_text_into_chunks(text, max_len=3500)
        logging.info(f"Synthesizing {len(text)} chars across {len(text_chunks)} chunks with model={model}, voice={voice}...")
        
        usage = {"prompt_token_count": 0, "candidates_token_count": 0, "total_token_count": 0}
        combined_audio_frames = b""
        
        try:
            import io
            for idx, chunk in enumerate(text_chunks):
                logging.info(f"Synthesizing VertexTTS single-speaker chunk {idx+1}/{len(text_chunks)}...")
                parts = []
                if system_instruction:
                    parts.append(f"Context: {system_instruction}\n\nTask: Read this text naturally.")
                else:
                     parts.append("Please read this text out loud naturally:")
                     
                parts.append(chunk)

                response = _generate_content_with_retry(
                    model=model,
                    contents=parts,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice
                                )
                            ),
                            language_code=language
                        )
                    )
                )

                if response.candidates and response.candidates[0].content.parts:
                     for part in response.candidates[0].content.parts:
                        if part.inline_data:
                            with wave.open(io.BytesIO(part.inline_data.data), 'rb') as w:
                                combined_audio_frames += w.readframes(w.getnframes())
                            
                     if response.usage_metadata:
                         usage["prompt_token_count"] += response.usage_metadata.prompt_token_count
                         usage["candidates_token_count"] += response.usage_metadata.candidates_token_count
                         usage["total_token_count"] += response.usage_metadata.total_token_count
                else:
                    logging.warning(f"No audio returned for chunk {idx+1}.")

            if combined_audio_frames:
                with wave.open(output_file, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(combined_audio_frames)
                logging.info(f"Audio saved to {output_file}")
                return output_file, {"state": "completed"}, usage
            else:
                logging.warning("No audio returned.")
                return None, {"state": "error", "details": "No audio content"}, usage
                
        except Exception as e:
            logging.error(f"Error: {e}")
            return None, {"state": "error", "details": str(e)}, usage

    def synthesize_replicated_voice(self, text, reference_audio_bytes, project_id, location="us-central1", output_file="output_cloned.wav", apply_dictionary=True, language="fr-FR"):
        try:
            if apply_dictionary:
                text = apply_pronunciation_dictionary(text)
            
            encoded_audio = base64.b64encode(reference_audio_bytes).decode("utf-8")
            
            local_client = genai.Client(vertexai=True, project=project_id, location=location)

            logging.info("Generating replicated voice content...")
            response = local_client.models.generate_content(
                model="gemini-2.5-flash-tts-eap-11-2025",
                contents=f"Say the following: {text}",
                config=types.GenerateContentConfig(
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            replicated_voice_config=types.ReplicatedVoiceConfig(
                                voice_sample_audio=encoded_audio
                            )
                        ),
                        language_code=language
                    ),
                    response_modalities=["AUDIO"],
                ),
            )

            if not response.candidates or not response.candidates[0].content.parts:
                 raise ValueError("No audio content generated.")

            audio_data = response.candidates[0].content.parts[0].inline_data.data
            
            with wave.open(output_file, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(audio_data)
                
            logging.info(f"Replicated voice audio saved to {output_file}")
            
            usage = {
                "prompt_token_count": response.usage_metadata.prompt_token_count,
                "candidates_token_count": response.usage_metadata.candidates_token_count,
                "total_token_count": response.usage_metadata.total_token_count
            } if response.usage_metadata else {}

            return output_file, {"state": "completed"}, usage

        except Exception as e:
            logging.error(f"Error in synthesize_replicated_voice: {e}")
            return None, {"state": "error", "details": str(e)}, {}

class CloudTTSProvider(TTSProvider):
    def synthesize_multi_speaker(self, dialogue, model=None, voice_main=None, voice_sidebar=None, output_file="output_multi.wav", strict_mode=False, prompt_main=PROMPT_ANCHOR, prompt_sidebar=PROMPT_REPORTER, seed=None, temperature=None, apply_dictionary=True, delay_seconds=0, language="fr-FR", progress_callback=None):
        if model is None: model = DEFAULT_MODEL_SYNTH
        if voice_main is None: voice_main = DEFAULT_VOICE_MAIN
        if voice_sidebar is None: voice_sidebar = DEFAULT_VOICE_SIDEBAR

        logging.info(f"Synthesizing multi-speaker (Cloud TTS) to {output_file}")
        
        try:
            client_cloud = texttospeech.TextToSpeechClient()
        except NameError:
            logging.error("google.cloud.texttospeech is not imported.")
            return None, {"state": "error", "details": "Dependency missing"}, {}
            
        custom_pronunciations = None
        pseudo_dict = {}
        applied_ipa = {}
        if apply_dictionary:
            p_dict = load_pronunciation_dictionary()
            pseudo_dict, ipa_params, applied_ipa = prepare_tts_dictionaries(p_dict, provider_type="cloudtts")
            
            if ipa_params:
                custom_pronunciations = texttospeech.CustomPronunciations(
                    pronunciations=ipa_params
                )

        prompt_instruction = prompt_main if dialogue and dialogue[0].get("speaker") == "R" else PROMPT_ANCHOR
        if strict_mode:
            prompt_instruction += " Read the text EXACTLY as written, word for word. Do not add or remove anything."
            
        # Cloud TTS has a strict 4000 byte limit for prompt + turns text combined.
        prompt_bytes = len(prompt_instruction.encode('utf-8'))
        max_batch_bytes = 3800 - prompt_bytes  # Leave 200 bytes for JSON/Proto overhead
        
        batches = []
        current_batch = []
        current_bytes = 0
        
        for i, seg in enumerate(dialogue):
            text = seg["text"]
            if pseudo_dict:
                # We reuse the utility specifically telling it what dictionary to use
                text = apply_pronunciation_dictionary(text, pseudo_dict)
                
            speaker = seg["speaker"]
            if not text.strip(): continue
            
            alias = "Speaker1" if speaker == "R" else "Speaker2"
            
            # Split dynamically to ensure no single chunk can possibly exceed the max bytes
            safe_chunk_char_limit = int(max_batch_bytes / 2.5) # estimate: 2.5 bytes per char worst-case (French accents)
            for chunk in split_text_into_chunks(text, max_len=safe_chunk_char_limit):
                chunk_bytes = len(chunk.encode('utf-8'))
                
                # If a chunk is SOMEHOW still too big (extremely dense utf-8), force split it.
                if chunk_bytes > max_batch_bytes:
                    chunk = chunk[:int(max_batch_bytes/3)]
                    chunk_bytes = len(chunk.encode('utf-8'))
                
                if current_bytes + chunk_bytes > max_batch_bytes and current_batch:
                    batches.append(current_batch)
                    current_batch = []
                    current_bytes = 0
                    
                current_batch.append(texttospeech.MultiSpeakerMarkup.Turn(text=chunk, speaker=alias))
                current_bytes += chunk_bytes
                
        if current_batch:
            batches.append(current_batch)
            
        multi_speaker_voice_config = texttospeech.MultiSpeakerVoiceConfig(
            speaker_voice_configs=[
                texttospeech.MultispeakerPrebuiltVoice(speaker_alias="Speaker1", speaker_id=voice_main),
                texttospeech.MultispeakerPrebuiltVoice(speaker_alias="Speaker2", speaker_id=voice_sidebar),
            ]
        )
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=language, model_name=model, multi_speaker_voice_config=multi_speaker_voice_config,
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16, sample_rate_hertz=24000)
        
        combined_audio_frames = b""
        usage = {"prompt_token_count": 0, "candidates_token_count": 0, "total_token_count": 0}
        
        try:
            import io
            from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
            
            def should_retry_cloud_tts(exception):
                error_str = str(exception).lower()
                # Do not retry deterministically failing requests
                if "custom pronunciation phrases are invalid" in error_str:
                    return False
                if "400 " in error_str and "sensitive" not in error_str:
                    return False
                return True
                
            @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=2, max=30), retry=retry_if_exception(should_retry_cloud_tts), reraise=True)
            def _synthesize_batch(s_input, v, a_config):
                return client_cloud.synthesize_speech(input=s_input, voice=v, audio_config=a_config)

            for b_idx, batch in enumerate(batches):
                logging.info(f"Synthesizing CloudTTS multi-speaker batch {b_idx+1}/{len(batches)}...")
                    
                synthesis_input = texttospeech.SynthesisInput(
                    multi_speaker_markup=texttospeech.MultiSpeakerMarkup(turns=batch),
                    prompt=prompt_instruction,
                    custom_pronunciations=custom_pronunciations
                )
                
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = _synthesize_batch(synthesis_input, voice, audio_config)
                        break
                    except Exception as e:
                        error_str = str(e)
                        match = re.search(r"custom pronunciation phrases are invalid:\s+(.*?)(?:\. Please|$)", error_str)
                        if match and custom_pronunciations and attempt < max_retries - 1:
                            invalid_phrases_raw = match.group(1)
                            invalid_phrases = [p.strip() for p in invalid_phrases_raw.split(',')]
                            logging.warning(f"Invalid custom pronunciations detected: {invalid_phrases}. Removing and retrying (Attempt {attempt+1}/{max_retries}).")
                            
                            new_pronunciations = [p for p in custom_pronunciations.pronunciations if p.phrase not in invalid_phrases]
                            
                            if apply_dictionary:
                                p_dict = load_pronunciation_dictionary()
                                updated = False
                                for bad_phrase in invalid_phrases:
                                    if bad_phrase in p_dict:
                                        del p_dict[bad_phrase]
                                        updated = True
                                        logging.info(f"Removed invalid phrase '{bad_phrase}' from global dictionary.")
                                if updated:
                                    save_pronunciation_dictionary(p_dict)
                            
                            if new_pronunciations:
                                custom_pronunciations = texttospeech.CustomPronunciations(pronunciations=new_pronunciations)
                                synthesis_input.custom_pronunciations = custom_pronunciations
                            else:
                                custom_pronunciations = None
                                synthesis_input = texttospeech.SynthesisInput(
                                    multi_speaker_markup=texttospeech.MultiSpeakerMarkup(turns=batch),
                                    prompt=prompt_instruction
                                )
                        else:
                            raise e
                
                with wave.open(io.BytesIO(response.audio_content), 'rb') as w:
                    combined_audio_frames += w.readframes(w.getnframes())
                
                if progress_callback:
                    progress_callback(b_idx + 1, len(batches), response.audio_content)
                
                if delay_seconds > 0 and b_idx < len(batches) - 1:
                    combined_audio_frames += b'\x00' * int(delay_seconds * 48000)
                    
            if combined_audio_frames:
                with wave.open(output_file, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(combined_audio_frames)
            logging.info(f"Multi-speaker audio saved to {output_file}")
            return output_file, {"state": "completed", "applied_ipa_phonemes": applied_ipa}, usage
        except Exception as e:
             logging.error(f"Error in CloudTTS multi-speaker: {e}")
             return None, {"state": "error", "details": str(e)}, usage

    def synthesize_and_save(self, text, model=None, voice=None, output_file="output.wav", apply_dictionary=True, system_instruction=None, language="fr-FR", progress_callback=None):
        if model is None: model = DEFAULT_MODEL_SYNTH
        if voice is None: voice = DEFAULT_VOICE_MAIN
        
        logging.info(f"Synthesizing single speaker (Cloud TTS) to {output_file}")
        
        try:
            client_cloud = texttospeech.TextToSpeechClient()
        except NameError:
            logging.error("google.cloud.texttospeech is not imported.")
            return None, {"state": "error", "details": "Dependency missing"}, {}
            
        custom_pronunciations = None
        pseudo_dict = {}
        applied_ipa = {}
        if apply_dictionary:
            p_dict = load_pronunciation_dictionary()
            pseudo_dict, ipa_params, applied_ipa = prepare_tts_dictionaries(p_dict, provider_type="cloudtts")
            
            if ipa_params:
                custom_pronunciations = texttospeech.CustomPronunciations(
                    pronunciations=ipa_params
                )
    
        prompt_instruction = ""
        if system_instruction:
            prompt_instruction = f"Context: {system_instruction}\n\nTask: Read this text naturally."
        else:
            prompt_instruction = "Please read this text out loud naturally:"
            
        if pseudo_dict:
            text = apply_pronunciation_dictionary(text, pseudo_dict)
            
        # Cloud TTS max size is 4000 bytes, EXCEPT for Flash-Lite which is 512 bytes.
        is_flash_lite = ("flash-lite" in model.lower())
        prompt_bytes = len(prompt_instruction.encode('utf-8'))
        
        if is_flash_lite:
            max_batch_bytes = 480 - prompt_bytes # Strict 512 bytes limit for Flash-Lite
        else:
            max_batch_bytes = 3800 - prompt_bytes # Standard 4000 bytes limit
            
        safe_chunk_char_limit = int(max_batch_bytes / 2.5)
        
        # Ensure we don't end up with negative chunk limits if the prompt is massive
        if safe_chunk_char_limit < 50:
            safe_chunk_char_limit = 50
            
        text_chunks = split_text_into_chunks(text, safe_chunk_char_limit)
        
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language,
            name=voice,
            model_name=model
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=24000
        )
        
        usage = {"prompt_token_count": 0, "candidates_token_count": 0, "total_token_count": 0}
        combined_audio_frames = b""
        
        try:
            import io
            from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
            
            def should_retry_cloud_tts_single(exception):
                error_str = str(exception).lower()
                if "custom pronunciation phrases are invalid" in error_str:
                    return False
                if "400 " in error_str and "sensitive" not in error_str:
                    return False
                return True
                
            @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=2, max=30), retry=retry_if_exception(should_retry_cloud_tts_single), reraise=True)
            def _synthesize_single_chunk(s_input, v, a_config):
                return client_cloud.synthesize_speech(input=s_input, voice=v, audio_config=a_config)

            for idx, chunk in enumerate(text_chunks):
                logging.info(f"Synthesizing CloudTTS single-speaker chunk {idx+1}/{len(text_chunks)}...")
                synthesis_input = texttospeech.SynthesisInput(text=chunk, prompt=prompt_instruction, custom_pronunciations=custom_pronunciations)
                
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = _synthesize_single_chunk(synthesis_input, voice_params, audio_config)
                        break
                    except Exception as e:
                        error_str = str(e)
                        match = re.search(r"custom pronunciation phrases are invalid:\s+(.*?)(?:\. Please|$)", error_str)
                        if match and custom_pronunciations and attempt < max_retries - 1:
                            invalid_phrases_raw = match.group(1)
                            invalid_phrases = [p.strip() for p in invalid_phrases_raw.split(',')]
                            logging.warning(f"Invalid custom pronunciations detected: {invalid_phrases}. Removing and retrying (Attempt {attempt+1}/{max_retries}).")
                            
                            new_pronunciations = [p for p in custom_pronunciations.pronunciations if p.phrase not in invalid_phrases]
                            
                            if apply_dictionary:
                                p_dict = load_pronunciation_dictionary()
                                updated = False
                                for bad_phrase in invalid_phrases:
                                    if bad_phrase in p_dict:
                                        del p_dict[bad_phrase]
                                        updated = True
                                        logging.info(f"Removed invalid phrase '{bad_phrase}' from global dictionary.")
                                if updated:
                                    save_pronunciation_dictionary(p_dict)
                            
                            if new_pronunciations:
                                custom_pronunciations = texttospeech.CustomPronunciations(pronunciations=new_pronunciations)
                                synthesis_input.custom_pronunciations = custom_pronunciations
                            else:
                                custom_pronunciations = None
                                synthesis_input.custom_pronunciations = None
                        else:
                            raise e
                with wave.open(io.BytesIO(response.audio_content), 'rb') as w:
                    combined_audio_frames += w.readframes(w.getnframes())
                    
                if progress_callback:
                    progress_callback(idx + 1, len(text_chunks), response.audio_content)

            if combined_audio_frames:
                with wave.open(output_file, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(combined_audio_frames)
                    
            logging.info(f"Audio saved to {output_file}")
            return output_file, {"state": "completed", "applied_ipa_phonemes": applied_ipa}, usage
        except Exception as e:
             logging.error(f"Error in CloudTTS single-speaker: {e}")
             return None, {"state": "error", "details": str(e)}, usage

    def synthesize_replicated_voice(self, text, reference_audio_bytes, project_id, location="us-central1", output_file="output_cloned.wav", apply_dictionary=True, language="fr-FR"):
        logging.info("Cloud TTS uses Vertex AI fallback for voice replication")
        fallback_provider = VertexTTSProvider()
        return fallback_provider.synthesize_replicated_voice(
            text, reference_audio_bytes, project_id, location, output_file, apply_dictionary, language
        )

def split_text_into_chunks(text, max_len=3500):
    """Splits a single large text into smaller chunks for the TTS API payload limits."""
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

# === TTS Provider Interface ===
class TTSFactory:
    @staticmethod
    def get_provider() -> TTSProvider:
        provider_type = os.getenv("TTS_PROVIDER", "cloudtts").lower()
        if provider_type == "cloudtts":
            return CloudTTSProvider()
        elif provider_type == "vertexai":
            return VertexTTSProvider()
        else:
            logging.error(f"Unknown TTS provider: {provider_type}")
            return None

# Wrapper functions
def synthesize_multi_speaker(dialogue, model=None, voice_main=None, voice_sidebar=None, output_file="output_multi.wav", strict_mode=False, prompt_main=PROMPT_ANCHOR, prompt_sidebar=PROMPT_REPORTER, seed=None, temperature=None, apply_dictionary=True, delay_seconds=0, language="fr-FR", progress_callback=None):
    return TTSFactory.get_provider().synthesize_multi_speaker(
        dialogue, model, voice_main, voice_sidebar, output_file, strict_mode, prompt_main, prompt_sidebar, seed, temperature, apply_dictionary, delay_seconds, language, progress_callback
    )

def synthesize_and_save(text, model=None, voice=None, output_file="output.wav", apply_dictionary=True, system_instruction=None, language="fr-FR", progress_callback=None):
    provider = TTSFactory.get_provider()
    return provider.synthesize_and_save(text, model, voice, output_file, apply_dictionary, system_instruction, language, progress_callback)

def synthesize_replicated_voice(text, reference_audio_bytes, project_id, location="us-central1", output_file="output_cloned.wav", apply_dictionary=True, language="fr-FR"):
    return TTSFactory.get_provider().synthesize_replicated_voice(
        text, reference_audio_bytes, project_id, location, output_file, apply_dictionary, language
    )

if __name__ == "__main__":
    # Parameters that were in the notebook calls
    # URL = "https://www.lefigaro.fr/en/in-dubai-where-more-and-more-french-flock-to-start-a-new-life-20260124"
    URL = "https://www.lefigaro.fr/international/en-direct-iran-donald-trump-ali-khamenei-armees-europe-terroristes-erfan-soltani-manifestations-ormuz-20260202"
    MODEL_NAME = "gemini-2.5-pro-tts"
    VOICE_NAME = "Aoede"
    
    # Create assets directory if it doesn't exist
    if not os.path.exists("./assets"):
        os.makedirs("./assets")

    OUTPUT_FILE = os.path.join("./assets", convert_url_to_file_name(URL) + ".wav")

    OUTPUT_FILE = os.path.join("./assets", convert_url_to_file_name(URL) + ".wav")

    logging.info(f"Fetching {URL}...")
    text_content = extract_text_from_url(URL)

    if text_content:
        logging.info(f"Extracted {len(text_content)} characters.")
        
        # 1. Parse Structure
        logging.info("Analyzing text structure with Gemini...")
        dialogue, usage = parse_text_structure(text_content, model="gemini-2.5-flash")
        
        if dialogue:
            # 1.1 Enrich dialogue with prompts
            for seg in dialogue:
                if seg.get("speaker") == "R":
                    seg["prompt"] = PROMPT_ANCHOR
                else:
                    seg["prompt"] = PROMPT_REPORTER

            # 1.5 Export dialogue to JSON
            json_filename = OUTPUT_FILE.replace(".wav", ".json")
            with open(json_filename, "w", encoding='utf-8') as f:
                json.dump(dialogue, f, indent=4, ensure_ascii=False)
            logging.info(f"Article structure exported to {json_filename}")

            # 2. Synthesize Multi-Speaker
            VOICE_SIDEBAR_NAME = "Fenrir"
            synthesize_multi_speaker(
                dialogue,
                model=MODEL_NAME,
                voice_main=VOICE_NAME,
                voice_sidebar=VOICE_SIDEBAR_NAME,
                output_file=OUTPUT_FILE
            )
        else:
            logging.error("Failed to parse structure, falling back to single speaker.")
            synthesize_and_save(text_content, model=MODEL_NAME, voice=VOICE_NAME, output_file=OUTPUT_FILE)
    else:
        logging.error("Failed to extract text.")
