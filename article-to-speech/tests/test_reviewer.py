"""
Tests for the reviewer module.
"""
import pytest
from unittest.mock import patch, MagicMock
from api.reviewer import review_recording

def test_review_recording_success():
    """Test successful review of audio recording."""
    mock_response = MagicMock()
    mock_response.text = "Mocked review feedback\nScore: 5/5"
    
    with patch("api.reviewer.vertex_client") as mock_client:
        mock_client.models.generate_content.return_value = mock_response
        
        audio_bytes = b"dummy audio data"
        prompt = "Read in a serious tone"
        
        feedback = review_recording(audio_bytes, prompt)
        
        assert "Mocked review feedback" in feedback
        assert "Score: 5/5" in feedback
        mock_client.models.generate_content.assert_called_once()

def test_review_recording_no_client():
    """Test behavior when client is not initialized."""
    with patch("api.reviewer.vertex_client", None):
        feedback = review_recording(b"data", "prompt")
        assert "Error: Client not initialized." in feedback
