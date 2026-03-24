import os
os.environ["GOOGLE_CLOUD_PROJECT"] = "customer-demo-01"
from api import extract_text_from_url, extract_text_from_url_with_gemini
import logging

logging.basicConfig(level=logging.INFO)

url = "https://www.lefigaro.fr/politique/j-ai-pris-la-decision-d-etre-candidat-de-la-place-beauvau-a-la-conquete-de-l-elysee-la-mue-presidentielle-de-bruno-retailleau-20260212"

print("--- Standard Extraction ---")
text_std = extract_text_from_url(url)
if text_std:
    print(f"Length: {len(text_std)}")
    print(text_std[:500])
else:
    print("Standard Extraction Failed")

print("\n--- Gemini Extraction ---")
text_gem, usage, truncated = extract_text_from_url_with_gemini(url)
if text_gem:
    print(f"Length: {len(text_gem)}")
    print(text_gem[:500])
else:
    print("Gemini Extraction Failed")
