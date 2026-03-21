import pytest
from dotenv import load_dotenv
load_dotenv()

from unittest.mock import patch, MagicMock
from gemini_url_to_audio import research_pronunciations


@patch('gemini_url_to_audio.client')
def test_research_pronunciations(mock_client):
    mock_response = MagicMock()
    mock_response.text = '[{"term": "Shein", "pronunciation": "chiine"}]'
    mock_client.models.generate_content.return_value = mock_response

    text = "Je soutiens François Fillon pour cette élection et j'achète chez Shein."
    res, usage = research_pronunciations(text, model="gemini-2.5-flash")
    
    assert res is not None, "Research pronunciations did not return a response"
    assert isinstance(res, list), "Response should be a list of dictionaries"
    
    terms_found = [item.get("term") for item in res if isinstance(item, dict)]
    assert "Shein" in terms_found or "Fillon" in terms_found, f"Missing expected terms from the response. Found: {terms_found}"
