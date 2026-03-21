import os
import pytest
from gemini_url_to_audio import synthesize_and_save

def test_language_parameter():
    """
    Test that the language parameter is accepted and a file is generated.
    We'll use a short English text and request en-US.
    """
    text = "Hello, this is a test for the language parameter."
    output_file = "assets/test_lang_en.wav"
    
    # Ensure assets dir exists
    if not os.path.exists("assets"):
        os.makedirs("assets")
        
    # Clean up previous run
    if os.path.exists(output_file):
        os.remove(output_file)
        
    outfile, status, usage = synthesize_and_save(
        text,
        output_file=output_file,
        language="en-US"
    )
    
    assert outfile == output_file
    assert status["state"] == "completed"
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 1000 # Should be non-empty
    
    print(f"Details: {status}")
    print(f"Usage: {usage}")

if __name__ == "__main__":
    test_language_parameter()
    print("Test passed!")
