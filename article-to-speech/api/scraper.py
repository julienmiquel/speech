import requests
import logging
import re
from google.genai import types
from bs4 import BeautifulSoup
from api.config import vertex_client, DEFAULT_MODEL_PARSE
from prompts import EXTRACT_CONTENT_PROMPT
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def _generate_content_with_retry(model, contents, config=None):
    if config:
        return vertex_client.models.generate_content(model=model, contents=contents, config=config)
    else:
        return vertex_client.models.generate_content(model=model, contents=contents)

def extract_text_from_url(url: str):
    """
    Extracts text content from a given URL using BeautifulSoup.
    """
    logging.info(f"Fetching URL (Standard): {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        logging.error(f"Error fetching URL: {e}")
        #return None

    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        logging.info(f"Standard extraction successful. Length: {len(text)}")
        return text
    except Exception as e:
        logging.error(f"Error parsing with BeautifulSoup: {e}")
        return None

def extract_text_from_url_with_gemini(url: str, parsing_model: str = None):
    """
    Extracts text content from a URL using Gemini.
    """
    if parsing_model is None:
        parsing_model = DEFAULT_MODEL_PARSE
    logging.info(f"Fetching URL (Gemini): {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None, {}, False
        
    if not vertex_client:
        logging.error("Vertex AI Client not initialized.")
        return None, {}, False

    try:
        prompt = EXTRACT_CONTENT_PROMPT
        clean_html = re.sub(r'<(script|style).*?>.*?</\1>', '', html_content, flags=re.DOTALL)
        is_truncated = len(clean_html) > 500000
        
        response = _generate_content_with_retry(
            model=parsing_model,
            contents=[prompt, clean_html[:500000]],
            config=types.GenerateContentConfig(response_mime_type="text/plain")
        )
        
        usage = {
            "prompt_token_count": response.usage_metadata.prompt_token_count,
            "candidates_token_count": response.usage_metadata.candidates_token_count,
            "total_token_count": response.usage_metadata.total_token_count
        } if response.usage_metadata else {}
        
        return response.text.strip(), usage, is_truncated
    except Exception as e:
        logging.error(f"Error extracting with Gemini for URL {url}: {e}")
        return None, {}, False
