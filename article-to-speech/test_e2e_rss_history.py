import requests
import time
import sys

API_URL = "http://127.0.0.1:8000"

def test_rss_to_history():
    print("1) Fetching Figaro RSS...")
    import xml.etree.ElementTree as ET
    res = requests.get("https://www.lefigaro.fr/rss/figaro_actualites.xml")
    root = ET.fromstring(res.text)
    items = root.findall(".//item")
    if not items:
        print("Empty RSS feed.")
        sys.exit(1)
        
    # Try up to 5 items to find a non-paywalled/valid article
    dialogue = None
    successful_url = None
    for item in items[:5]:
        first_url = item.find("link").text
        print(f"-> Testing URL: {first_url}")
        
        payload_auto = {
            "url": first_url,
            "method": "gemini",
            "model_parse": "gemini-2.5-flash",
            "language": "fr-FR"
        }
        r = requests.post(f"{API_URL}/automate/async", json=payload_auto)
        r.raise_for_status()
        auto_job_id = r.json()["job_id"]
        
        while True:
            status_res = requests.get(f"{API_URL}/jobs/{auto_job_id}").json()
            if status_res["status"] == "completed":
                print(f"-> task completed")
                break
            if status_res["status"] == "error":
                print("Automation Error:", status_res)
                break
            time.sleep(1)
            print(f"-> wait task to complete")
            
        if status_res["status"] == "completed" and status_res["result"].get("dialogue"):
            dialogue = status_res["result"]["dialogue"]
            successful_url = first_url
            break
        else:
            print("No dialogue generated for this article, trying next...")
            
    if not dialogue:
        print("Failed to extract dialogue from any of the first 5 RSS items. Falling back to Wikipedia...")
        first_url = "https://fr.wikipedia.org/wiki/Croissant"
        successful_url = first_url
        print(f"-> Testing URL: {first_url}")
        
        payload_auto = {
            "url": first_url,
            "method": "gemini",
            "model_parse": "gemini-2.5-flash",
            "language": "fr-FR"
        }
        r = requests.post(f"{API_URL}/automate/async", json=payload_auto)
        r.raise_for_status()
        auto_job_id = r.json()["job_id"]
        
        while True:
            status_res = requests.get(f"{API_URL}/jobs/{auto_job_id}").json()
            if status_res["status"] == "completed":
                break
            if status_res["status"] == "error":
                print("Automation Error:", status_res)
                sys.exit(1)
            time.sleep(1)
            
        dialogue = status_res["result"].get("dialogue")
        if not dialogue:
            print("Fallback failed.")
            sys.exit(1)
        
    print(f"\n3) Submitting to /synthesize/async (Audio Generation) for {successful_url}...")
    payload_synth = {
        "text": "\n".join([d["text"] for d in dialogue]),
        "is_multi_speaker": False,
        "dialogue_segments": dialogue,
        "voice": "fr-FR-Neural2-B",
        "output_filename": f"test_rss_{int(time.time())}.wav",
        "url": successful_url,
        "mode": "Automation",
        "extraction_method": "API Test"
    }
    
    r = requests.post(f"{API_URL}/synthesize/async", json=payload_synth)
    r.raise_for_status()
    synth_job_id = r.json()["job_id"]
    
    while True:
        status_res = requests.get(f"{API_URL}/jobs/{synth_job_id}").json()
        if status_res["status"] == "completed":
            break
        if status_res["status"] == "error":
            print("Synthesis Error:", status_res)
            sys.exit(1)
        time.sleep(1)
        
    audio_path = status_res["result"]["audio_url"]
    print(f"-> Audio Generated: {audio_path}")
    
    print("\n4) Verifying /history for the new entry...")
    # Add a slight delay to ensure file system sync
    time.sleep(1)
    
    r = requests.get(f"{API_URL}/history")
    history = r.json()["history"]
    
    found = False
    for item in history:
        if item.get("audio_file") == audio_path and item.get("url") == successful_url:
            found = True
            break
            
    if found:
        print("✅ SUCCESS! The new generation entry is correctly registered in the API History.")
    else:
        print("❌ FAILURE! The entry was NOT found in /history.")
        sys.exit(1)

if __name__ == "__main__":
    test_rss_to_history()
