import pytest
from unittest.mock import patch, MagicMock
import json
from gemini_url_to_audio import parse_text_structure, intelligent_chunk

def test_intelligent_chunk_basic():
    """Test that it doesn't split short text."""
    text = "Short text."
    chunks = intelligent_chunk(text, max_length=100)
    assert chunks == [text]

def test_intelligent_chunk_split_paragraphs():
    """Test splitting by paragraphs."""
    text = "Para 1.\n\nPara 2."
    chunks = intelligent_chunk(text, max_length=10)
    assert len(chunks) == 2
    assert chunks[0] == "Para 1."
    assert chunks[1] == "Para 2."

def test_intelligent_chunk_hard_split():
    """Test hard split when no delimiters found."""
    text = "A" * 10
    chunks = intelligent_chunk(text, max_length=3)
    assert len(chunks) == 4
    assert all(len(c) <= 3 for c in chunks)

@patch('gemini_url_to_audio.client')
def test_parse_text_structure_success(mock_client):
    """Test successful parsing of text into segments."""
    mock_gen_response = MagicMock()
    mock_gen_response.text = json.dumps([
        {"text": "Main story paragraph 1.", "type": "main"},
        {"text": "An insert about data.", "type": "sidebar"},
        {"text": "Main story paragraph 2.", "type": "main"}
    ])
    mock_gen_response.usage_metadata = None
    mock_client.models.generate_content.return_value = mock_gen_response
    
    dialogue, usage, is_truncated = parse_text_structure("Some input text")
    
    assert len(dialogue) == 3
    assert dialogue[0]["speaker"] == "R"
    assert dialogue[1]["speaker"] == "S"
    assert dialogue[2]["speaker"] == "R"
    assert dialogue[1]["text"] == "An insert about data."

@patch('gemini_url_to_audio.client')
def test_parse_text_structure_chunking(mock_client):
    """Test that segments are chunked if they exceed 4000 chars."""
    long_text = "L" * 5000
    mock_gen_response = MagicMock()
    mock_gen_response.text = json.dumps([
        {"text": long_text, "type": "main"}
    ])
    mock_gen_response.usage_metadata = None
    mock_client.models.generate_content.return_value = mock_gen_response
    
    dialogue, usage, is_truncated = parse_text_structure("input")
    
    # It should be split into at least 2 chunks (max 4000 each)
    assert len(dialogue) >= 2
    assert all(len(d["text"]) <= 4000 for d in dialogue)
    assert all(d["speaker"] == "R" for d in dialogue)
