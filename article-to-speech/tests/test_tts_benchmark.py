import pytest
import os
import time
import json
import logging
import glob
from gemini_url_to_audio import TTSFactory

os.makedirs("assets/tmp", exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global dict to hold all results from the various tests
_benchmark_results = {}

@pytest.fixture(scope="module", autouse=True)
def benchmark_results_manager():
    """Fixture to handle saving the JSON results after all tests in this file run."""
    yield
    output_json = "tts_benchmark_results.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(_benchmark_results, f, indent=4, ensure_ascii=False)
    logging.info(f"--- All Benchmark results written to {output_json} ---")


def _init_provider_results(provider_name):
    if provider_name not in _benchmark_results:
        _benchmark_results[provider_name] = {
            "provider": provider_name,
            "single_speaker": {},
            "multi_speaker": {},
            "large_article_tests": []
        }

@pytest.mark.parametrize("provider_name", ["vertexai", "cloudtts"])
def test_performance_single_speaker(provider_name):
    _init_provider_results(provider_name)
    os.environ["TTS_PROVIDER"] = provider_name
    provider = TTSFactory.get_provider()
    
    text = "Ceci est un test de performance pour mesurer la vitesse de génération vocale." * 5
    outfile = f"assets/tmp/test_{provider_name}_single.wav"
    
    start_time = time.time()
    _, status, _ = provider.synthesize_and_save(text=text, output_file=outfile, apply_dictionary=False)
    duration = time.time() - start_time
    
    _benchmark_results[provider_name]["single_speaker"] = {
        "status": status.get("state"),
        "details": status.get("details", ""),
        "duration_seconds": round(duration, 2),
        "output_file": outfile,
        "chars_processed": len(text)
    }
    
    assert status.get("state") == "completed", f"Single speaker failed for {provider_name}"


@pytest.mark.parametrize("provider_name", ["vertexai", "cloudtts"])
def test_performance_multi_speaker(provider_name):
    _init_provider_results(provider_name)
    os.environ["TTS_PROVIDER"] = provider_name
    provider = TTSFactory.get_provider()
    
    dialogue = [
        {"text": "Bonjour, comment allez-vous aujourd'hui ?", "speaker": "R"},
        {"text": "Je vais très bien, merci de le demander.", "speaker": "S"},
        {"text": "C'est une excellente nouvelle. Continuons notre test.", "speaker": "R"}
    ]
    outfile = f"assets/tmp/test_{provider_name}_multi.wav"
    
    start_time = time.time()
    _, status, _ = provider.synthesize_multi_speaker(dialogue=dialogue, output_file=outfile, apply_dictionary=False)
    duration = time.time() - start_time
    
    _benchmark_results[provider_name]["multi_speaker"] = {
        "status": status.get("state"),
        "details": status.get("details", ""),
        "duration_seconds": round(duration, 2),
        "output_file": outfile,
        "segments_processed": len(dialogue)
    }
    
    assert status.get("state") == "completed", f"Multi speaker failed for {provider_name}"


def get_cached_files():
    cache_dir = "assets/cache"
    if not os.path.exists(cache_dir):
        return []
    files = glob.glob(os.path.join(cache_dir, "*.txt"))
    # Sort files by size
    files_with_size = [(f, os.path.getsize(f)) for f in files]
    files_with_size.sort(key=lambda x: x[1])
    # To avoid extremely long test times, we limit to the 2 smallest cached files for normal runs
    # (The user can edit this array to run more files as needed)
    return files_with_size[:2]

CACHE_FILES = get_cached_files()

@pytest.mark.parametrize("provider_name", ["vertexai", "cloudtts"])
@pytest.mark.parametrize("file_path, size", CACHE_FILES)
def test_article_limits(provider_name, file_path, size):
    _init_provider_results(provider_name)
    os.environ["TTS_PROVIDER"] = provider_name
    provider = TTSFactory.get_provider()
    
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        
    outfile = f"assets/tmp/test_limit_{provider_name}_{len(text)}.wav"
    
    start_time = time.time()
    # Test limits using synthesize_and_save
    _, status, _ = provider.synthesize_and_save(text=text, output_file=outfile, apply_dictionary=False)
    duration = time.time() - start_time
    
    # We append the results so they appear in large_article_tests
    _benchmark_results[provider_name]["large_article_tests"].append({
        "status": status.get("state"),
        "details": status.get("details", ""),
        "duration_seconds": round(duration, 2),
        "output_file": outfile,
        "size_chars": len(text),
        "file": os.path.basename(file_path)
    })
    
    # Asserting completion for cloudtts.
    # Note: vertexai truncates text > 4000 characters and may sometimes fail with generic errors randomly.
    # We allow the test to log the results even if it asserts false.
    assert status.get("state") == "completed", f"Limit test failed for {provider_name} on {file_path}"

@pytest.mark.parametrize("provider_name", ["vertexai", "cloudtts"])
def test_extreme_limit_10k(provider_name):
    """Synthetic test injecting 10,000 characters into the TTS engine."""
    _init_provider_results(provider_name)
    os.environ["TTS_PROVIDER"] = provider_name
    provider = TTSFactory.get_provider()
    
    # Generate 10k characters
    base_text = "Voici une phrase de test pour valider la limite de dix mille caractères du synthétiseur vocal. "
    repetitions = (10000 // len(base_text)) + 1
    text = (base_text * repetitions)[:10000]
    
    outfile = f"assets/tmp/test_limit_{provider_name}_10k.wav"
    
    start_time = time.time()
    _, status, _ = provider.synthesize_and_save(text=text, output_file=outfile, apply_dictionary=False)
    duration = time.time() - start_time
    
    _benchmark_results[provider_name]["large_article_tests"].append({
        "status": status.get("state"),
        "details": status.get("details", ""),
        "duration_seconds": round(duration, 2),
        "output_file": outfile,
        "size_chars": len(text),
        "file": "synthetic_10000_chars.txt"
    })
    
    assert status.get("state") == "completed", f"10k limit test failed for {provider_name}"
