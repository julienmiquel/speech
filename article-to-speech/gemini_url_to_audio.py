import sys
import os
import requests
import re
from google import genai
from google.genai import types
import json
import wave
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Authenticate (Colab specific, kept for compatibility if run in Colab environment)
if "google.colab" in sys.modules:
    from google.colab import auth
    auth.authenticate_user()

# Configure Project and Client
# Set your project ID here
PROJECT_ID = "customer-demo-01" 
LOCATION = "us-central1"

if not PROJECT_ID or PROJECT_ID == "[your-project-id]":
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

# Initialize Vertex AI Client
try:
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    logging.info(f"Initialized Vertex AI client for project: {PROJECT_ID}, location: {LOCATION}")
except Exception as e:
    logging.error(f"Failed to initialize client: {e}")
    client = None

# Prompt Definitions
PROMPT_ANCHOR = "You are a professional news anchor reading a breaking news story. You speak FR-fr. Read this text with a serious, engaging, and clear tone. Maintain a steady pace suitable for a news broadcast."
PROMPT_REPORTER = "You are a field reporter providing additional context and details. You speak FR-fr. Read this text in an informative, slightly distinct tone, differentiating it from the main headline news."

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

def extract_text_from_url_with_gemini(url, parsing_model="gemini-2.5-flash"):
    """
    Extracts text content from a URL using Gemini 2.5 Flash.
    """
    logging.info(f"Fetching URL (Gemini): {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        logging.error(f"Error fetching URL: {e}")
        return None

    if not client:
        logging.error("Vertex AI Client not initialized.")
        return None

    try:
        prompt = """
        You are an expert web scraper and content extractor.
        Extract the MAIN ARTICLE TEXT from the following HTML content.
        
        Rules:
        1. Remove all navigation menus, footers, sidebars, and advertisements.
        2. Remove all scripts, styles, and code snippets.
        3. Determine the main headline and body text.
        4. Return ONLY the clean, readable text of the article. Do not add any introductory or concluding remarks.
        5. Maintain the natural paragraph structure.
        """
        
        # Pre-clean HTML to remove massive script/style blocks before sending to Gemini
        # This significantly reduces payload size and latency
        clean_html = re.sub(r'<(script|style).*?>.*?</\1>', '', html_content, flags=re.DOTALL)
        
        logging.info(f"HTML Content length (Raw): {len(html_content)}")
        logging.info(f"HTML Content length (Cleaned): {len(clean_html)}")

        response = client.models.generate_content(
            model=parsing_model,
            contents=[prompt, clean_html[:100000]], # Send up to 100k chars of CLEAN html
            config=types.GenerateContentConfig(
                response_mime_type="text/plain"
            )
        )
        logging.info(f"Gemini extraction successful. Length: {len(response.text.strip())}")
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error extracting with Gemini: {e}")
        return None

def convert_url_to_file_name(url):
    """Converts a URL into a safe filename string."""
    # Remove protocol and replace non-alphanumeric characters with underscores
    clean_url = re.sub(r'^https?://', '', url)
    clean_url = re.sub(r'^www\.', '', clean_url)
    clean_url = re.sub(r'^lefigaro.fr\.', '', clean_url)
    return re.sub(r'[^a-zA-Z0-9]', '_', clean_url).strip('_')


def parse_text_structure(text, model="gemini-2.5-flash", strict_mode=False, system_prompt=None):
    """
    Uses a Flash model to separate the main text from 'encarts' (sidebars/inserts).
    Returns a list of segments: [{"text": "...", "speaker": "A"}, {"text": "...", "speaker": "B"}]
    Speaker A = Main text, Speaker B = Encarts
    """
    if not client:
        logging.error("Client not initialized.")
        return None
    
    # Truncate parsing context if HUGE, but usually we need full context. 
    # Flash has a large context window, so 100k chars should be fine.
    
    if system_prompt:
        prompt = system_prompt
    else:
        prompt = f"""
    You are an expert content analyzer.
    Analyze the following article text. Identify the main narrative text and any RELEVANT 'encarts' (e.g. quotes, important explanatory boxes).
    Exlude any content that corresponds to:
    - Navigation menus
    - Links/URLs not part of the narrative
    - Irrelevant sidebars or ads

    Output a JSON list of objects, where each object represents a continuous segment of text.
    Each object must have:
    - "text": The exact text content of the segment.
    - "type": "main" for main article text, or "sidebar" for relevant encarts.
    
    Maintain the original reading order. Merge adjacent segments of the same type.
    """

        if not strict_mode:
            prompt += """
    IMPORTANT: To improve the reading flow, insert the following tags into the "text" content where appropriate:
    - [short pause] : Insert this tag between distinct list items or short clauses to create a natural breathing pause.
    - [medium pause] : Insert this tag between major sentences or distinct ideas.
    - [long pause] : Insert this tag before a significant topic change or dramatic statement.
    
    You MAY also use the following "Vocal Tags" (use sparingly, only if the text content heavily supports the emotion):
    - [curious] : Use for questions or intriguing statements.
    - [scared] : Use for frightening content.
    - [bored] : Use for monotonous content.
    
    CRITICAL: Ensure every "text" segment ends with a period (.) if it does not already end with a punctuation mark.
    
    Do NOT use these tags excessively, only where they improve the natural rhythm of a news reading.
            """
        else:
            prompt += """
    CRITICAL: STRICT MODE ENABLED.
    - Do NOT change a single word of the original text.
    - Do NOT add any pauses, vocal tags, or extra punctuation.
    - Do NOT remove any text unless it is clearly navigation/menu/ad garbage.
    - The "text" field MUST match the original content EXACTLY word-for-word.
            """

    prompt += f"""
    Article Text (Truncated for analysis if necessary):
    {text[:5000]} 
    """
    
    import time
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            json_text = response.text
            # Clean up code blocks if model returns them (though mime_type json usually prevents this)
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.strip().endswith("```"):
                json_text = json_text.strip()[:-3]
                
            segments = json.loads(json_text)
            
            # Map to speakers
            dialogue = []
            for seg in segments:
                speaker = "R" if seg.get("type") == "main" else "S" # R = Reader (Main), S = Sidebar
                dialogue.append({"text": seg.get("text"), "speaker": speaker})
                
            return dialogue
        except Exception as e:
            logging.warning(f"Error parsing text structure (Attempt {attempt+1}/3): {e}")
            if "429" in str(e):
                time.sleep(5 * (attempt + 1))
            else:
                break
    return None

def synthesize_multi_speaker(dialogue, model="gemini-2.5-pro", voice_main="Aoede", voice_sidebar="Fenrir", output_file="output_multi.wav", strict_mode=False, prompt_main=PROMPT_ANCHOR, prompt_sidebar=PROMPT_REPORTER, seed=None, temperature=None):
    """
    Synthesizes multi-speaker audio from a dialogue list.
    dialogue: [{"text": "...", "speaker": "R"}, ...]
    """
    if not client:
        return None
        
    logging.info(f"Synthesizing multi-speaker audio with {len(dialogue)} segments...")
    
    # Construct the multi-speaker markup (using explicit speaker turns if supported, 
    # or just constructing the prompt as a script for the model to perform).
    # Gemini 2.5 TTS supports multi-speaker via 'turns' or just text with Speaker labels if prompted correctly.
    # However, 'speech_config' with 'voice_name' applies to the whole request usually.
    # We will use the 'multi-speaker' prompting capabilities of the model itself if utilizing the context window,
    # OR we need to verify if the SDK supports `multi_speaker_config`.
    
    # Check if we can do 'multi_speaker_config'. The current SDK 'types' might not fully expose it in a simple way
    # or the model `gemini-2.5-pro-preview-tts` might handle it via prompt + config.
    # Actually, for 2.5 TTS, we should use speaker diarization in the prompt or look for multi-speaker config.
    # As of recent updates, usually you provide the text with speaker labels and a config mapping speakers to voices.
    
    # Let's try to find the `PrebuiltVoiceConfig` equivalent for multi-speaker.
    # If not readily available in 'types' inspection, we might need to iterate.
    # BUT, the user prompt asked to use Gemini to *generate* a reading.
    
    # The standard way currently is to instruct the model.
    # "Speaker A: Hello. Speaker B: Hi there."
    # And providing voice config for speakers if the API supports it.
    
    # Given the constraint of the current `types` we saw earlier, let's look at what we used:
    # `types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice))`
    
    # NOTE: As of the known 'gemini-2.5-pro-preview-tts' capabilities, it can do multi-speaker if you format text as:
    # "Speaker A: ... \n Speaker B: ..." and potentially just ask it to use different voices.
    # However, rigorous control usually requires the API.
    # Let's try to simply concatenate the text with labels and ask it to distinguish voices, 
    # OR generate separate chunks and merge audio (safer/more robust for now?).
    
    # User Request: "Genere une lecture avec 2 speaker en separant le texte principal (speaker 1) et les encarts (speaker 2)"
    # Using separate generation and merging is guaranteed to work with current simple API usage.
    # BUT user said "utilise gemini flash 3... genere une lecture".
    
    # Approach: Generate separate audio clips for each segment and concatenate them.
    # This ensures exact voice control (Speaker 1 = Voice A, Speaker 2 = Voice B).
    
    combined_audio = b""
    
    # Create a new wave file to write to eventually, but we need to merge PCM data.
    # We know the format is 24kHz, 16bit, 1 channel.
    
    for i, seg in enumerate(dialogue):
        text = seg["text"]
        speaker = seg["speaker"]
        voice = voice_main if speaker == "R" else voice_sidebar
        
        logging.info(f"Segment {i}: Speaker {speaker} ({voice}) - {len(text)} chars")
        if not text.strip():
            continue
            
        # Use the prompt from the segment if available, otherwise use the passed arguments
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
            # Prepare configuration
            config_params = {
                "response_modalities": ["AUDIO"],
                "speech_config": types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice
                        )
                    )
                )
            }
            
            if seed is not None:
                config_params["seed"] = seed
                
            if temperature is not None:
                config_params["temperature"] = temperature

            response = client.models.generate_content(
                model=model,
                contents=f"{prompt_instruction} Text to read: {text}",
                config=types.GenerateContentConfig(**config_params)
            )
            
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        combined_audio += part.inline_data.data
        except Exception as e:
            logging.error(f"Error generating audio for segment {i}: {e}")
            
    if combined_audio:
         with wave.open(output_file, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(24000)
            wf.writeframes(combined_audio)
         logging.info(f"Multi-speaker audio saved to {output_file}")
         return output_file
         
    return None
def synthesize_and_save(text, model="gemini-2.5-pro", voice="Aoede", output_file="output.wav"):
    """
    Synthesizes speech from text and saves to a file.
    """
    if not client:
        logging.error("Client not initialized.")
        return None

    logging.info(f"Synthesizing {len(text)} chars with model={model}, voice={voice}...")
    
    # Truncate for demo if huge
    if len(text) > 4000:
        logging.warning("Text > 4000 chars, truncating for demo purposes.")
        text = text[:4000]

    try:
        response = client.models.generate_content(
            model=model,
            contents=f"Please read this text out loud naturally: {text}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice
                        )
                    )
                )
            )
        )

        if response.candidates and response.candidates[0].content.parts:
             for part in response.candidates[0].content.parts:
                if part.inline_data:
                    audio_bytes = part.inline_data.data
                    # Vertex AI returns raw PCM (24kHz, 1 channel, 16bit)
                    # We must wrap it in a WAV container.
                    with wave.open(output_file, "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2) # 16-bit
                        wf.setframerate(24000)
                        wf.writeframes(audio_bytes)
                    logging.info(f"Audio saved to {output_file}")
                    return output_file
        logging.warning("No audio returned.")
        return None
    except Exception as e:
        logging.error(f"Error: {e}")
        return None

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
        dialogue = parse_text_structure(text_content, model="gemini-2.5-flash")
        
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
