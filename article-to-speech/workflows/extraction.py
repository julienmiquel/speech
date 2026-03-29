import requests
import xml.etree.ElementTree as ET
import logging
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def fetch_rss_feed(url="https://www.lefigaro.fr/rss/figaro_actualites.xml", fallback_no_title="Sans Titre", fallback_no_desc="Pas de description"):
    """
    Fetches and parses an RSS feed, returning a list of dictionaries.
    """
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        items = []
        for item in root.findall('.//item')[:60]:
            title_el = item.find('title')
            link_el = item.find('link')
            desc_el = item.find('description')
            items.append({
                "title": title_el.text if title_el is not None else fallback_no_title,
                "link": link_el.text if link_el is not None else "",
                "description": desc_el.text if desc_el is not None else fallback_no_desc
            })
        return items
    except Exception as e:
        logging.error(f"Erreur RSS: {e}")
        return []

def perform_extraction(url, method, model_parse):
    """
    Business logic for extracting an article by calling the API. 
    Returns: (text, is_cached, usage, is_truncated, error_message)
    """
    logging.info(f"Checking cache or starting extraction for URL via API: {url}")
    
    try:
        req_method = "gemini" if "gemini" in method.lower() else "bs4"
        res = requests.post(f"{API_BASE_URL}/extract", json={"url": url, "method": req_method})
        res.raise_for_status()
        
        data = res.json()
        if "text" in data and data["text"]:
            return data["text"], False, data.get("usage", {}), data.get("is_truncated", False), None
        else:
            return None, False, None, False, "API returned empty text."
    except Exception as e:
         logging.error(f"Extraction failed: {e}")
         return None, False, None, False, str(e)
