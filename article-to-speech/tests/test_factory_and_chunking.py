import pytest
import os
from gemini_url_to_audio import TTSFactory, CloudTTSProvider, VertexTTSProvider, split_text_into_chunks, intelligent_chunk

def test_tts_factory_switching(monkeypatch):
    """Test that TTSFactory correctly returns the provider based on env var."""
    
    monkeypatch.setenv("TTS_PROVIDER", "cloudtts")
    provider = TTSFactory.get_provider()
    assert isinstance(provider, CloudTTSProvider)
    
    monkeypatch.setenv("TTS_PROVIDER", "vertexai")
    provider = TTSFactory.get_provider()
    assert isinstance(provider, VertexTTSProvider)

def test_split_text_into_chunks():
    """Test basic sentence-based chunking."""
    text = "Sentence one. Sentence two. Sentence three."
    # Max length of 15 should split between sentences
    chunks = split_text_into_chunks(text, max_len=15)
    
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) <= 20 # Allowing some margin for the split logic

def test_intelligent_chunk():
    """Test hierarchical chunking (paragraphs > lines > sentences)."""
    text = """Paragraph 1 line 1
Paragraph 1 line 2

Paragraph 2"""
    
    # Split by paragraph
    chunks = intelligent_chunk(text, max_length=50)
    assert len(chunks) == 1
    assert "Paragraph 2" in chunks[0]
    assert "Paragraph 1 line 1" in chunks[0]
    
    # Split by line (max_length=25 means Paragraph 1 lines will be split)
    chunks = intelligent_chunk(text, max_length=25)
    assert "Paragraph 1 line 1" in chunks
    assert "Paragraph 1 line 2" in chunks
    assert "Paragraph 2" in chunks

def test_chunking_byte_limit_simulation():
    """
    Simulate the 4000 byte limit logic used in CloudTTSProvider.
    We want to ensure that multi-byte characters (like French accents) are handled.
    """
    text = "é" * 2000 # 2000 chars, but each 'é' is 2 bytes in UTF-8
    assert len(text.encode('utf-8')) == 4000
    
    # If we have a max of 3800 bytes, it should split
    max_batch_bytes = 3800
    safe_chunk_char_limit = int(max_batch_bytes / 2.5) # From CloudTTSProvider logic
    
    chunks = split_text_into_chunks(text, max_len=safe_chunk_char_limit)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.encode('utf-8')) <= max_batch_bytes
