import pytest
import sys
import os
from gemini_url_to_audio import extract_text_from_url

# Presets extracted from app.py (excluding broken ones)
PRESETS = [
    ("Long Article", "https://en.wikipedia.org/wiki/Artificial_intelligence"),
    ("Editorial", "https://en.wikipedia.org/wiki/Machine_learning"),
    ("Economy", "https://en.wikipedia.org/wiki/Economy"),
    ("Interview", "https://en.wikipedia.org/wiki/Interview"),
    ("International", "https://en.wikipedia.org/wiki/International"), # 404
    ("Brands", "https://en.wikipedia.org/wiki/Brand")
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
