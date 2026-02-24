import pytest
from gemini_url_to_audio import extract_text_from_url_with_gemini

def test_extract_text_from_url_with_gemini_bad_url():
    """
    Tests that providing an invalid or non-existent URL to the Gemini extractor
    returns the expected tuple (None, {}) so that the unpacking in app.py
    does not throw a TypeError.
    """
    # A known 404 URL or invalid URL
    bad_url = "https://www.lefigaro.fr/international/le-pentagone-prepare-le-deploiement-d-un-deuxieme-porte-avions-pour-accroitre-la-pression-sur-l-iran-selon-le-wall-street-journal-20260212"
    
    # We expect this to fail gracefully without crashing
    result = extract_text_from_url_with_gemini(bad_url)
    
    # Verify the result is exactly the tuple (None, {})
    assert type(result) is tuple, f"Expected a tuple, but got {type(result)}"
    assert len(result) == 3, f"Expected tuple of length 3, but got {len(result)}"
    
    text, usage, is_truncated = result
    assert text is None, "Expected text to be None on failure"
    assert usage == {}, "Expected usage to be empty dict on failure"
