import pytest
import os
from unittest.mock import MagicMock, patch
from STT.stt_providers.gemini import GeminiSTTProvider

@pytest.fixture
def mock_genai():
    with patch("google.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client

def test_gemini_provider_init(mock_genai):
    provider = GeminiSTTProvider(model_name="gemini-3.1-pro-preview")
    assert provider.model_name == "gemini-3.1-pro-preview"
    assert provider.location == "us-central1"

def test_gemini_provider_transcribe(mock_genai):
    provider = GeminiSTTProvider(model_name="gemini-3.1-pro-preview")
    
    # Mock response
    mock_response = MagicMock()
    mock_response.text = "Hello world"
    mock_genai.models.generate_content.return_value = mock_response
    
    # Mock chunk_audio_with_vad to return a single chunk
    with patch("STT.stt_providers.gemini.chunk_audio_with_vad") as mock_vad:
        mock_vad.return_value = [b"dummy_audio_bytes"]
        
        result = provider.transcribe(audio_path="dummy_path.wav")
        
        assert result == "Hello world"
        mock_genai.models.generate_content.assert_called_once()

def test_gemini_provider_transcribe_with_data(mock_genai):
    provider = GeminiSTTProvider(model_name="gemini-3.1-pro-preview")
    
    # Mock response
    mock_response = MagicMock()
    mock_response.text = "Hello world"
    mock_genai.models.generate_content.return_value = mock_response
    
    # Mock chunk_audio_with_vad to return a single chunk
    with patch("STT.stt_providers.gemini.chunk_audio_with_vad") as mock_vad:
        mock_vad.return_value = [b"dummy_audio_bytes"]
        
        result = provider.transcribe(audio_data=b"dummy_audio_data")
        
        assert result == "Hello world"
        mock_genai.models.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_gemini_provider_transcribe_async(mock_genai):
    provider = GeminiSTTProvider(model_name="gemini-3.1-pro-preview")
    
    # Mock response
    mock_response = MagicMock()
    mock_response.text = "Hello world"
    mock_genai.models.generate_content.return_value = mock_response
    
    # Mock chunk_audio_with_vad to return a single chunk
    with patch("STT.stt_providers.gemini.chunk_audio_with_vad") as mock_vad:
        mock_vad.return_value = [b"dummy_audio_bytes"]
        
        result = await provider.transcribe_async(audio_path="dummy_path.wav")
        
        assert result == "Hello world"
        mock_genai.models.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_gemini_provider_transcribe_async_with_data(mock_genai):
    provider = GeminiSTTProvider(model_name="gemini-3.1-pro-preview")
    
    # Mock response
    mock_response = MagicMock()
    mock_response.text = "Hello world"
    mock_genai.models.generate_content.return_value = mock_response
    
    # Mock chunk_audio_with_vad to return a single chunk
    with patch("STT.stt_providers.gemini.chunk_audio_with_vad") as mock_vad:
        mock_vad.return_value = [b"dummy_audio_bytes"]
        
        result = await provider.transcribe_async(audio_data=b"dummy_audio_data")
        
        assert result == "Hello world"
        mock_genai.models.generate_content.assert_called_once()
