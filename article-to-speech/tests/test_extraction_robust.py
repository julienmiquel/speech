import pytest
from unittest.mock import patch, MagicMock
import requests
from gemini_url_to_audio import extract_text_from_url_with_gemini

@patch('requests.get')
def test_extract_with_gemini_request_failure(mock_get):
    """Test handling of network errors."""
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")
    
    text, usage, is_truncated = extract_text_from_url_with_gemini("https://error.com")
    
    assert text is None
    assert usage == {}
    assert is_truncated is False

@patch('requests.get')
@patch('gemini_url_to_audio.client')
def test_extract_with_gemini_empty_html(mock_client, mock_get):
    """Test handling of empty HTML content."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = ""
    mock_get.return_value = mock_response
    
    # We expect it to still try to send to Gemini if it's empty (though maybe it should bail early)
    mock_gen_response = MagicMock()
    mock_gen_response.text = ""
    mock_gen_response.usage_metadata = None
    mock_client.models.generate_content.return_value = mock_gen_response
    
    text, usage, is_truncated = extract_text_from_url_with_gemini("https://empty.com")
    
    assert text == ""
    assert usage == {}
    assert is_truncated is False

@patch('requests.get')
@patch('gemini_url_to_audio.client')
def test_extract_with_gemini_api_error(mock_client, mock_get):
    """Test handling of Gemini API errors."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Some content</body></html>"
    mock_get.return_value = mock_response
    
    mock_client.models.generate_content.side_effect = Exception("API quota exceeded")
    
    text, usage, is_truncated = extract_text_from_url_with_gemini("https://api-error.com")
    
    assert text is None
    assert usage == {}
    assert is_truncated is False

@patch('requests.get')
@patch('gemini_url_to_audio.client')
def test_extract_with_gemini_truncation(mock_client, mock_get):
    """Test that it correctly identifies truncation for large HTML."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Create HTML > 500,000 chars
    large_html = "<html><body>" + ("A" * 500001) + "</body></html>"
    mock_response.text = large_html
    mock_get.return_value = mock_response
    
    mock_gen_response = MagicMock()
    mock_gen_response.text = "Extracted"
    mock_gen_response.usage_metadata = None
    mock_client.models.generate_content.return_value = mock_gen_response
    
    text, usage, is_truncated = extract_text_from_url_with_gemini("https://large.com")
    
    assert is_truncated is True
    # Verify it only sent 500,000 chars to Gemini
    # contents=[prompt, clean_html[:500000]]
    call_args = mock_client.models.generate_content.call_args
    sent_content = call_args[1]['contents'][1]
    assert len(sent_content) == 500000

@patch('requests.get')
@patch('gemini_url_to_audio.client')
def test_extract_with_gemini_html_cleaning(mock_client, mock_get):
    """Test that script and style tags are removed before sending to Gemini."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    html_with_scripts = """
    <html>
    <head><style>body { color: red; }</style></head>
    <body>
    <script>alert('hello');</script>
    <p>Main content</p>
    </body>
    </html>
    """
    mock_response.text = html_with_scripts
    mock_get.return_value = mock_response
    
    mock_gen_response = MagicMock()
    mock_gen_response.text = "Main content"
    mock_gen_response.usage_metadata = None
    mock_client.models.generate_content.return_value = mock_gen_response
    
    extract_text_from_url_with_gemini("https://cleaning.com")
    
    call_args = mock_client.models.generate_content.call_args
    sent_content = call_args[1]['contents'][1]
    
    assert "<script>" not in sent_content
    assert "<style>" not in sent_content
    assert "Main content" in sent_content
