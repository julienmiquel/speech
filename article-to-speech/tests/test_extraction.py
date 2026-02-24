import pytest
from dotenv import load_dotenv
load_dotenv()

from unittest.mock import patch, MagicMock
from gemini_url_to_audio import extract_text_from_url, extract_text_from_url_with_gemini


TEST_URL = "https://www.lefigaro.fr/vox/economie/l-editorial-de-gaetan-de-capele-strategie-energetique-il-faut-sanctuariser-le-nucleaire-20260211"

def test_extract_text_from_url_standard():
    text = extract_text_from_url(TEST_URL)
    assert text is not None, "Standard extraction failed to return text"
    assert len(text) > 0, "Extracted text is empty"

@patch('gemini_url_to_audio.client')
def test_extract_text_from_url_gemini(mock_client):
    mock_response = MagicMock()
    mock_response.text = "Mocked extracted text"
    mock_response.usage_metadata.prompt_token_count = 10
    mock_client.models.generate_content.return_value = mock_response

    text, usage, is_truncated = extract_text_from_url_with_gemini(TEST_URL)
    assert text is not None, "Gemini extraction failed to return text"
    assert len(text) > 0, "Extracted text is empty"
    assert isinstance(usage, dict), "Usage should be a dictionary"
