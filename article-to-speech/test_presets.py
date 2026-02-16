import pytest
import sys
import os
from gemini_url_to_audio import extract_text_from_url

# Presets extracted from app.py (excluding broken ones)
PRESETS = [
    ("Long Article", "https://www.lefigaro.fr/politique/j-ai-pris-la-decision-d-etre-candidat-de-la-place-beauvau-a-la-conquete-de-l-elysee-la-mue-presidentielle-de-bruno-retailleau-20260212"),
    ("Editorial", "https://www.lefigaro.fr/vox/economie/l-editorial-de-gaetan-de-capele-strategie-energetique-il-faut-sanctuariser-le-nucleaire-20260211"),
    ("Economy", "https://www.lefigaro.fr/conjoncture/l-industrie-automobile-francaise-a-perdu-un-tiers-de-ses-effectifs-entre-2010-et-2023-constate-l-insee-20260212"),
    ("Interview", "https://www.lefigaro.fr/musique/lord-kossity-le-rap-c-est-un-art-et-la-jeune-generation-fait-tout-sauf-du-rap-20260211"),
    ("International", "https://www.lefigaro.fr/international/le-pentagone-prepare-le-deploiement-d-un-deuxieme-porte-avions-pour-accroitre-la-pression-sur-l-iran-selon-le-wall-street-journal-20260212"), # 404
    ("Brands", "https://www.lefigaro.fr/conso/les-plateformes-d-ultra-fast-fashion-seduisent-toujours-plus-d-un-francais-sur-trois-en-2025-d-apres-une-etude-20260212")
]

@pytest.mark.parametrize("name,url", PRESETS)
def test_preset_extraction(name, url):
    """
    Verifies that the standard extraction works for a given URL.
    """
    print(f"\nTesting extraction for {name}: {url}")
    text = extract_text_from_url(url)
    
    assert text is not None, f"Failed to extract text from {name} ({url})"
    assert len(text) > 100, f"Extracted text too short for {name} (length: {len(text)})"
    print(f"Success! Extracted {len(text)} characters.")

if __name__ == "__main__":
    # Allow running directly with python
    for name, url in PRESETS:
        try:
            test_preset_extraction(name, url)
        except AssertionError as e:
            print(f"FAILED: {e}")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
