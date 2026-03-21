import pytest
from unittest.mock import patch, MagicMock
from google.cloud import texttospeech
from gemini_url_to_audio import CloudTTSProvider

@patch("gemini_url_to_audio.load_pronunciation_dictionary")
@patch("gemini_url_to_audio.texttospeech.TextToSpeechClient")
def test_cloud_tts_partitions_dictionary(mock_client_class, mock_load_dict):
    """
    Ensures that CloudTTSProvider filters out non-IPA dictionary entries 
    (containing hyphens or uppercase letters) from the CustomPronunciations object 
    and applies them instead via manual string replacement regex.
    """
    # 3 items: 1 true IPA, 2 pseudo-phonetics
    mock_load_dict.return_value = {
        "Fillon": "fijɔ̃",            # Valid IPA (should go to API)
        "Shein": "Chi-ine",           # Has Capital and hyphen (Pseudo to be stripped)
        "Fast-fashion": "fa-chion"    # Has hyphen (Pseudo to be stripped)
    }
    
    # Setup mock Google Cloud TTS client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.audio_content = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\xc0]\x00\x00\x80\xbb\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    mock_client.synthesize_speech.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    provider = CloudTTSProvider()
    provider.synthesize_and_save(
        "Fillon a parlé de Shein et de Fast-fashion.",
        model="test-model",
        voice="test-voice",
        output_file="dummy.wav",
        apply_dictionary=True
    )
    
    assert mock_client.synthesize_speech.called, "synthesize_speech API was not called"
    
    call_args = mock_client.synthesize_speech.call_args
    synthesis_input = call_args.kwargs.get("input")
    
    # Verification 1: The API CustomPronunciations should ONLY contain 1 valid item
    pronunciations = synthesis_input.custom_pronunciations.pronunciations
    assert len(pronunciations) == 1, f"Expected 1 valid IPA pronunciation passed to API, got {len(pronunciations)}"
    assert pronunciations[0].phrase == "Fillon"
    assert pronunciations[0].pronunciation == "fijɔ̃"
    
    # Verification 2: The manual string replacements should have modified the text explicitly
    # Expected: "Fillon" (left alone for API), "Shein" -> "Chi-ine", "Fast-fashion" -> "fa-chion"
    expected_text = "Fillon a parlé de Chi-ine et de fa-chion."
    assert synthesis_input.text == expected_text, f"Expected manual substitution to be applied inside text payload. Got {synthesis_input.text}"
    
    print("Test passed: Pseudo-phonetics appropriately partitioned and applied via Regex, leaving only IPA for the API.")

if __name__ == "__main__":
    pytest.main(["-v", __file__])
