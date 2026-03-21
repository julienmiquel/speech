import pytest
import re
from gemini_url_to_audio import apply_pronunciation_dictionary, load_pronunciation_dictionary, prepare_tts_dictionaries

# Mock dictionary for testing
MOCK_DICT = {
    "Shein": {
        "inline": "Chi-ine",
        "ipa": "ʃi.in"
    },
    "Temu": {
        "inline": "Ti-mou",
        "ipa": "ti.mu"
    },
    "SaaS": {
        "inline": "Sass",
        "ipa": ""
    },
    "IPAOnly": {
        "inline": "",
        "ipa": "i.pe.a"
    }
}

def test_inline_replacement_logic():
    """Test that 'inline' replacements are correctly applied via regex."""
    text = "J'achète sur Shein et Temu. Le SaaS est top."
    # We pass the MOCK_DICT specifically for testing
    result = apply_pronunciation_dictionary(text, MOCK_DICT)
    
    # Shein -> Chi-ine (inline)
    # Temu -> Ti-mou (inline)
    # SaaS -> Sass (inline)
    # IPAOnly should NOT be replaced in the text because it only has IPA
    assert "Chi-ine" in result
    assert "Ti-mou" in result
    assert "Sass" in result
    assert "Shein" not in result
    assert "Temu" not in result
    assert "SaaS" not in result

def test_prepare_tts_dictionaries_cloudtts():
    """Verify Cloud TTS dictionary preparation (IPA priority)."""
    pseudo_dict, ipa_params, applied_ipa = prepare_tts_dictionaries(MOCK_DICT, provider_type="cloudtts")
    
    # Shein and Temu have IPA, so they should NOT be in pseudo_dict
    assert "Shein" not in pseudo_dict
    assert "Temu" not in pseudo_dict
    assert "IPAOnly" not in pseudo_dict
    
    # SaaS has NO IPA, so it SHOULD be in pseudo_dict
    assert pseudo_dict["SaaS"] == "Sass"
    
    # IPA params should contain Shein, Temu, and IPAOnly
    ipa_phrases = [p.phrase for p in ipa_params]
    assert "Shein" in ipa_phrases
    assert "Temu" in ipa_phrases
    assert "IPAOnly" in ipa_phrases
    assert "SaaS" not in ipa_phrases

def test_prepare_tts_dictionaries_vertexai():
    """Verify Vertex AI dictionary preparation (Inline fallback)."""
    pseudo_dict, ipa_params, applied_ipa = prepare_tts_dictionaries(MOCK_DICT, provider_type="vertexai")
    
    # Vertex AI doesn't support IPA, so everything with inline should be in pseudo_dict
    assert pseudo_dict["Shein"] == "Chi-ine"
    assert pseudo_dict["Temu"] == "Ti-mou"
    assert pseudo_dict["SaaS"] == "Sass"
    assert "IPAOnly" not in pseudo_dict
    
    # IPA params should be empty
    assert len(ipa_params) == 0
