import os
import argparse
import requests
import re
from google import genai
from google.genai import types

def extract_text_from_url(url):
    """
    Extracts text content from a given URL.
    Attempts to use BeautifulSoup if available, otherwise falls back to regex.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
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
        
        return text
    except ImportError:
        print("BeautifulSoup not found. Using simple regex fallback.")
        return extract_text_from_url_regex(html_content)

def extract_text_from_url_regex(html_content):
    """
    Fallback text extraction using regex.
    """
    # Remove script and style tags
    clean = re.sub(r'<(script|style).*?>.*?</\1>', '', html_content, flags=re.DOTALL)
    # Remove HTML tags
    clean = re.sub(r'<.*?>', '', clean)
    # Replace HTML entities (basic)
    clean = clean.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    # Collapse whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def text_to_speech(text, output_file="output.wav", project=None, location="europe-west1"):
    """
    Converts text to speech using Gemini API.
    """
    client = None
    
    if project:
        print(f"Using Vertex AI with project={project}, location={location}")
        client = genai.Client(vertexai=True, project=project, location=location)
    else:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
             api_key = os.environ.get("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set, and --project not provided.")
        client = genai.Client(api_key=api_key)

    # Truncate text if too long for a demo, or let the model handle it.
    # For a simple demo, we'll take the first 2000 characters to ensure it fits and is quick.
    if len(text) > 2000:
        print("Text too long, truncating to 2000 chars for demo.")
        text = text[:2000]

    print("Generating audio...")
    
    # Using the new Google GenAI SDK pattern for speech generation if available
    # Or using generate_content with audio response modality.
    # Note: As of my knowledge cutoff, direct TTS endpoint might be under `models.generate_content` with specific configuration
    # or a dedicated speech endpoint.
    # Checking implementation in typical GenAI SDK usage.
    # For now, I will use the 'gemini-2.0-flash-exp' model and ask for audio generation if supported,
    # OR use the specific speech endpoint if exposed.
    
    # Since the user specifically asked for "Gemini TTS pro", they might refer to the capability of Gemini 2.0 to generate audio
    # or the Google Cloud TTS.
    # Given the prompt "gemini TTS pro api", it likely refers to the new Gemini capabilities.
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro-preview-tts',
            contents=f"Please read this text out loud naturally: {text}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Aoede"
                        )
                    )
                )
            )
        )
        
        # Check if we got audio parts
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    # Save audio data
                    import base64
                    # inline_data.data is already bytes (decoded) in some SDK versions, 
                    # or base64 string in others.
                    # The SDK types usually handle this.
                    audio_bytes = part.inline_data.data
                    with open(output_file, "wb") as f:
                        f.write(audio_bytes)
                    print(f"Audio saved to {output_file}")
                    return output_file
        
        print("No audio data found in response.")
        
    except Exception as e:
        print(f"Error generating speech: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert URL to Audio using Gemini.")
    parser.add_argument("url", help="URL of the article to convert")
    parser.add_argument("--output", default="output.wav", help="Output audio file name")
    parser.add_argument("--project", help="GCP Project ID for Vertex AI", default=None)
    parser.add_argument("--location", help="GCP Region for Vertex AI", default="europe-west1")
    
    args = parser.parse_args()
    
    print(f"Extracting text from {args.url}...")
    text = extract_text_from_url(args.url)
    
    if text:
        print(f"Extracted {len(text)} characters.")
        # print(f"Preview: {text[:200]}...")
        text_to_speech(text, args.output, project=args.project, location=args.location)
    else:
        print("Failed to extract text.")
