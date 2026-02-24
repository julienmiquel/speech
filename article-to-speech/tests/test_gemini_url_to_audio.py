import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gemini_url_to_audio import (
    extract_text_from_url,
    synthesize_and_save,
    synthesize_multi_speaker,
    TTSFactory,
    VertexTTSProvider,
    CloudTTSProvider
)

@patch('gemini_url_to_audio.requests.get')
def test_extract_text_from_url(mock_get):
    mock_response = MagicMock()
    mock_response.text = "<html><body><p>Test content</p></body></html>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    text = extract_text_from_url("http://example.com")
    # extract_text_from_url cleans up HTML
    assert "Test content" in text
    assert len(text) > 0

@patch('gemini_url_to_audio.client')
def test_synthesize_and_save_vertex(mock_client):
    # Mock Vertex AI client behavior
    mock_response = MagicMock()
    mock_part = MagicMock()

    # Generate a valid wav in memory
    import io
    import wave
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(b'\x00\x00' * 100) # 100 frames of silence
    wav_data = buf.getvalue()

    mock_part.inline_data.data = wav_data
    mock_response.candidates = [MagicMock(content=MagicMock(parts=[mock_part]))]
    mock_client.models.generate_content.return_value = mock_response

    # Force Vertex provider
    with patch.dict(os.environ, {"TTS_PROVIDER": "vertexai"}):
        output_file, status, usage = synthesize_and_save(
            "Hello world",
            output_file="test_output.wav",
            progress_callback=lambda *args: print(args) # Should not raise TypeError
        )

    assert output_file == "test_output.wav"
    assert status["state"] == "completed"
    if os.path.exists("test_output.wav"):
        os.remove("test_output.wav")

@patch('gemini_url_to_audio.texttospeech.TextToSpeechClient')
def test_synthesize_and_save_cloud(mock_cloud_client_cls):
    # Mock Cloud TTS client
    mock_client = mock_cloud_client_cls.return_value
    mock_response = MagicMock()

    # Generate a valid wav in memory
    import io
    import wave
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(b'\x00\x00' * 100) # 100 frames of silence
    wav_data = buf.getvalue()

    mock_response.audio_content = wav_data
    mock_client.synthesize_speech.return_value = mock_response

    # Force Cloud provider
    with patch.dict(os.environ, {"TTS_PROVIDER": "cloudtts"}):
        output_file, status, usage = synthesize_and_save(
            "Hello world",
            output_file="test_output_cloud.wav",
            progress_callback=lambda *args: print(args) # Should not raise TypeError
        )

    assert output_file == "test_output_cloud.wav"
    assert status["state"] == "completed"
    if os.path.exists("test_output_cloud.wav"):
        os.remove("test_output_cloud.wav")
