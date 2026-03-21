import pytest
from unittest.mock import patch, MagicMock
from google.cloud import texttospeech
from gemini_url_to_audio import CloudTTSProvider

@patch("gemini_url_to_audio.load_pronunciation_dictionary")
@patch("gemini_url_to_audio.texttospeech.TextToSpeechClient")
def test_cloud_tts_deduplicates_dictionary(mock_client_class, mock_load_dict):
    """
    Ensures that CloudTTSProvider filters out dictionary entries that
    are case-insensitive duplicates (like 'Fast-fashion' and 'fast-fashion')
    to prevent Google Cloud TTS from throwing HTTP 400 errors.
    """
    mock_load_dict.return_value = {
        "Fast-fashion": "fastfaʃjɔ̃",
        "fast-fashion": "fastfaʃjɔ̃", # Duplicate!
        "Apple": "apɛl"
    }
    
    # Setup mock Google Cloud TTS client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.audio_content = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\xc0]\x00\x00\x80\xbb\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    mock_client.synthesize_speech.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    provider = CloudTTSProvider()
    provider.synthesize_and_save(
        "Voici de la fast-fashion et Apple.",
        model="test-model",
        voice="test-voice",
        output_file="dummy.wav",
        apply_dictionary=True
    )
    
    # Verify the mock API was triggered
    assert mock_client.synthesize_speech.called, "synthesize_speech API was not called"
    
    # Inspect arguments passed to the Google Cloud TTS API
    call_args = mock_client.synthesize_speech.call_args
    synthesis_input = call_args.kwargs.get("input")
    
    assert synthesis_input is not None
    assert synthesis_input.custom_pronunciations is not None
    
    # We provided 3 dict entries, but 2 are case-insensitive duplicates. 
    # The final payload should only contain 2 unique items.
    pronunciation_list = synthesis_input.custom_pronunciations.pronunciations
    assert len(pronunciation_list) == 2, f"Expected 2 deduplicated pronunciations, got {len(pronunciation_list)}"
    
    # Ensure none of them conflict
    phrases = [p.phrase.lower() for p in pronunciation_list]
    assert len(phrases) == len(set(phrases)), "Filtered list still has case-insensitive duplicates!"
    
    print("Test passed: Successfully successfully stripped out duplicated keys for CustomPronunciations.")
    
if __name__ == "__main__":
    pytest.main(["-v", __file__])
