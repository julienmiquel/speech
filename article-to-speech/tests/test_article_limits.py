import os
import time
import json
import logging
import glob
from gemini_url_to_audio import TTSFactory

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_limits_on_articles():
    providers = ["cloudtts", "vertexai"]
    cache_dir = "assets/cache"
    
    # Get all txt files in cache, sorted by size
    files = glob.glob(os.path.join(cache_dir, "*.txt"))
    files_with_size = [(f, os.path.getsize(f)) for f in files]
    files_with_size.sort(key=lambda x: x[1])
    
    results = []
    
    for file_path, size in files_with_size:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            
        logging.info(f"\n{'='*50}")
        logging.info(f"Testing Article: {os.path.basename(file_path)} (Size: {size} chars)")
        logging.info(f"{'='*50}")
        
        file_results = {
            "file": os.path.basename(file_path),
            "size_chars": len(text),
            "providers": {}
        }
        
        for provider_name in providers:
            os.environ["TTS_PROVIDER"] = provider_name
            provider = TTSFactory.get_provider()
            
            logging.info(f"--- Testing Provider: {provider_name} ---")
            
            # Test Single Speaker
            try:
                start_time = time.time()
                outfile = f"test_limit_{provider_name}_{len(text)}.wav"
                
                # We test synthesize_and_save because it sends the whole text at once
                # (CloudTTSProvider was updated to chunk it, let's see how Vertex behaves)
                output_file, status, usage = provider.synthesize_and_save(
                    text=text, 
                    output_file=outfile,
                    apply_dictionary=False
                )
                end_time = time.time()
                
                duration = end_time - start_time
                if status.get("state") == "completed":
                    logging.info(f"[{provider_name}] SUCCESS. Took {duration:.2f} seconds.")
                else:
                    logging.warning(f"[{provider_name}] RETURNED ERROR STATE: {status}")
                
                file_results["providers"][provider_name] = {
                    "status": status.get("state", "failed"),
                    "details": status.get("details", ""),
                    "duration_seconds": round(duration, 2),
                    "output_file": outfile
                }
            except Exception as e:
                logging.error(f"[{provider_name}] FAILED with exception: {e}")
                file_results["providers"][provider_name] = {
                    "status": "exception",
                    "error": str(e)
                }
                
        results.append(file_results)
        
    # Write results to JSON
    output_json = "article_limits_benchmark.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    logging.info(f"\n--- Limit Benchmark Complete ---")
    logging.info(f"Results written to {output_json}")

if __name__ == "__main__":
    test_limits_on_articles()
