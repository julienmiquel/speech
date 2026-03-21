import os
import time
import json
import logging
from gemini_url_to_audio import TTSFactory

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_provider(provider_type, text, dialogue):
    """Tests a specific TTS provider and returns speed metrics."""
    os.environ["TTS_PROVIDER"] = provider_type
    provider = TTSFactory.get_provider()
    
    if not provider:
        logging.error(f"Failed to load provider for {provider_type}")
        return None
        
    logging.info(f"--- Testing Provider: {provider_type} ---")
    
    results = {
        "provider": provider_type,
        "single_speaker": {},
        "multi_speaker": {}
    }
    
    # 1. Test Single Speaker
    try:
        start_time = time.time()
        outfile = f"test_{provider_type}_single.wav"
        output_file, status, usage = provider.synthesize_and_save(
            text=text, 
            output_file=outfile,
            apply_dictionary=False
        )
        end_time = time.time()
        
        duration = end_time - start_time
        logging.info(f"[{provider_type}] Single Speaker took {duration:.2f} seconds.")
        
        results["single_speaker"] = {
            "status": status.get("state", "failed"),
            "duration_seconds": round(duration, 2),
            "output_file": outfile,
            "chars_processed": len(text)
        }
    except Exception as e:
        logging.error(f"Single speaker test failed for {provider_type}: {e}")
        results["single_speaker"]["status"] = "error"
        results["single_speaker"]["error"] = str(e)
        
    # 2. Test Multi Speaker
    try:
        start_time = time.time()
        outfile = f"test_{provider_type}_multi.wav"
        output_file, status, usage = provider.synthesize_multi_speaker(
            dialogue=dialogue, 
            output_file=outfile,
            apply_dictionary=False
        )
        end_time = time.time()
        
        duration = end_time - start_time
        logging.info(f"[{provider_type}] Multi Speaker took {duration:.2f} seconds.")
        
        results["multi_speaker"] = {
            "status": status.get("state", "failed"),
            "duration_seconds": round(duration, 2),
            "output_file": outfile,
            "segments_processed": len(dialogue)
        }
    except Exception as e:
        logging.error(f"Multi speaker test failed for {provider_type}: {e}")
        results["multi_speaker"]["status"] = "error"
        results["multi_speaker"]["error"] = str(e)
        
    return results

if __name__ == "__main__":
    # Test data
    sample_text = "Ceci est un test de performance pour mesurer la vitesse de génération vocale." * 5
    sample_dialogue = [
        {"text": "Bonjour, comment allez-vous aujourd'hui ?", "speaker": "R"},
        {"text": "Je vais très bien, merci de le demander.", "speaker": "S"},
        {"text": "C'est une excellente nouvelle. Continuons notre test.", "speaker": "R"}
    ]
    
    providers_to_test = ["vertexai", "cloudtts"]
    all_results = {}
    
    for provider_name in providers_to_test:
        metrics = test_provider(provider_name, sample_text, sample_dialogue)
        if metrics:
            all_results[provider_name] = metrics
            
    # Write results to JSON
    output_json = "tts_benchmark_results.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)
        
    logging.info(f"\n--- Benchmark Complete ---")
    logging.info(f"Results have been written to {output_json}")
    
    # Print summary
    print("\n--- Summary ---")
    for provider, data in all_results.items():
        print(f"Provider: {provider}")
        if data["single_speaker"].get("status") == "completed":
            print(f"  Single Speaker Time: {data['single_speaker']['duration_seconds']}s")
        else:
            print(f"  Single Speaker Errors.")
            
        if data["multi_speaker"].get("status") == "completed":
            print(f"  Multi Speaker Time : {data['multi_speaker']['duration_seconds']}s")
        else:
            print(f"  Multi Speaker Errors.")
        print("-" * 20)
