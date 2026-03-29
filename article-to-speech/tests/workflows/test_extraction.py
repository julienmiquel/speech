import pytest
from unittest.mock import patch, MagicMock

from workflows.extraction import fetch_rss_feed, perform_extraction

@patch('workflows.extraction.requests.get')
def test_fetch_rss_feed_success(mock_get):
    class MockResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code
            
        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception("Network Error")

    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Test Feed</title>
            <item>
                <title>Article 1</title>
                <link>http://example.com/1</link>
                <description>Desc 1</description>
            </item>
            <item>
                <title>Article 2</title>
                <link>http://example.com/2</link>
                <!-- missing description -->
            </item>
        </channel>
    </rss>
    """
    mock_get.return_value = MockResponse(sample_xml, 200)

    items = fetch_rss_feed()
    assert len(items) == 2
    assert items[0]["title"] == "Article 1"
    assert items[0]["description"] == "Desc 1"
    assert items[1]["title"] == "Article 2"
    assert items[1]["description"] == "Pas de description" # Fallback usage

@patch('workflows.extraction.requests.get')
def test_fetch_rss_feed_error(mock_get):
    mock_get.side_effect = Exception("Connection Failed")
    
    items = fetch_rss_feed()
    assert items == []

@patch('workflows.extraction.requests.post')
def test_perform_extraction_cached(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"text": "Cached Content"}
    
    text, is_cached, usage, is_truncated, err = perform_extraction("http://example.com", "gemini", "model-test")
    
    assert is_cached is False
    assert text == "Cached Content"
    assert usage == {}
    assert is_truncated is False
    assert err is None

@patch('workflows.extraction.requests.post')
def test_perform_extraction_gemini_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "text": "Gemini Content",
        "usage": {"total_token_count": 10},
        "is_truncated": False
    }
    
    text, is_cached, usage, is_truncated, err = perform_extraction("http://example.com", "gemini", "model-test")
    
    assert is_cached is False
    assert text == "Gemini Content"
    assert usage["total_token_count"] == 10
    
    assert is_truncated is False
    assert err is None


@patch('workflows.extraction.requests.post')
def test_perform_extraction_standard_fails(mock_post):
    mock_post.side_effect = Exception("API failed completely")
    
    text, is_cached, usage, is_truncated, err = perform_extraction("http://example.com", "standard", "model-test")
    
    assert is_cached is False
    assert text is None
    assert err is not None

    
    assert is_cached is False
    assert text is None
    assert err is not None
