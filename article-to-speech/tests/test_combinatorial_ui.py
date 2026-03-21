import pytest
import os
import sys
import itertools
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from gemini_url_to_audio import synthesize_multi_speaker, synthesize_and_save

MODELS = [
    "gemini-2.5-flash-tts",
    "gemini-2.5-pro-tts",
    "gemini-2.5-flash-lite-preview-tts"
]

BOOLEANS = [True, False]

@pytest.mark.parametrize("model, apply_dictionary", list(itertools.product(MODELS, BOOLEANS)))
def test_single_speaker_synthesis_combinatorial(model, apply_dictionary):
    """Test generating single-speaker audio with different combinations of models and dictionary states."""
    text = "Bonjour, l'entreprise SaaS utilise beaucoup de RSE."
    output_file = f"test_single_{model.replace('.', '_')}_dict_{apply_dictionary}.wav"
    
    try:
        outfile, status, usage = synthesize_and_save(
            text=text,
            model=model,
            voice="Aoede",
            output_file=output_file,
            apply_dictionary=apply_dictionary
        )
        
        if status.get("state") == "error":
            if model == "gemini-2.5-flash-lite-preview-tts" and "512 bytes" in status.get("details", ""):
                # Flash-lite has a strict 512 byte limit that might easily trigger
                pass
            else:
                pytest.fail(f"Single-speaker {model} failed (dict={apply_dictionary}). Status: {status}")
        else:
            assert outfile is not None, f"Expected output file, got None. Status: {status}"
            assert os.path.exists(outfile), f"Output file does not exist: {outfile}"
            
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)
        
@pytest.mark.parametrize("model, apply_dictionary, strict_mode", list(itertools.product(MODELS, BOOLEANS, BOOLEANS)))
def test_multi_speaker_synthesis_combinatorial(model, apply_dictionary, strict_mode):
    """Test generating multi-speaker audio with different combinations of models, dictionary, and strict mode."""
    dialogue = [
        {"speaker": "R", "text": "Bienvenue dans cette démonstration de synthèse vocale complexe.", "prompt": ""},
        {"speaker": "S", "text": "En effet, nous testons les modèles avec des termes comme SaaS et RSE.", "prompt": ""}
    ]
    output_file = f"test_multi_{model.replace('.', '_')}_dict_{apply_dictionary}_strict_{strict_mode}.wav"    
    
    try:
        outfile, status, usage = synthesize_multi_speaker(
            dialogue=dialogue,
            model=model,
            voice_main="Aoede",
            voice_sidebar="Charon",
            output_file=output_file,
            apply_dictionary=apply_dictionary,
            strict_mode=strict_mode
        )
        
        if status.get("state") == "error":
            if model == "gemini-2.5-flash-lite-preview-tts":
                # Multi-speaker is known to be unsupported for flash-lite
                pass
            else:
                pytest.fail(f"Multi-speaker {model} failed (dict={apply_dictionary}, strict={strict_mode}). Status: {status}")
        else:    
            assert outfile is not None, f"Expected output file, got None. Status: {status}"
            assert os.path.exists(outfile), f"Output file does not exist: {outfile}"
            
    except Exception as e:
        if model == "gemini-2.5-flash-lite-preview-tts":
            pass
        else:
            pytest.fail(f"Exception during multi-speaker {model}: {str(e)}")
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)
