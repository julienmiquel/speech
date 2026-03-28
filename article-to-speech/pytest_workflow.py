import os
import time
import pytest
import requests
import xml.etree.ElementTree as ET
from async_helpers import async_dual_voice, async_single_voice
from job_manager import manager
from storage import RemoteStorage

# ---------------------------------------------------------
# CONFIGURATION (Adapt options based on your environment)
# ---------------------------------------------------------
RSS_INPUT_URL = "https://www.lefigaro.fr/rss/figaro_actualites.xml"
DEFAULT_MODEL_SYNTH = "gemini-2.5-pro-tts"
DEFAULT_VOICE_MAIN = "Aoede"
DEFAULT_VOICE_SIDEBAR = "Fenrir"

@pytest.fixture(scope="module")
def storage():
    """Initializes remote storage based on ENV variables."""
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "customer-demo-01")
    
    if not bucket_name:
        pytest.fail("GCS_BUCKET_NAME environment variable MUST be set to run this test.")
        
    return RemoteStorage(bucket_name, project_id)

def test_generate_from_rss_to_output_rss(storage):
    """
    Workflow checklist:
    1. Consume LeMonde RSS (Extract top article)
    2. Parse & Synthesize manually (replicate 'Automation' flow)
    3. Push output Wave on GCS & update remote metadata
    4. Verify public rss.xml gets a new <item>
    """
    # 1. AQUIRE ARTICLE FROM le figaro
    r = requests.get(RSS_INPUT_URL, timeout=15)
    assert r.status_code == 200, "Could not fetch Lemonde RSS feed"
    
    root = ET.fromstring(r.text)
    items = root.findall('.//item')
    assert len(items) > 0, "LeMonde RSS feed is empty?"
    
    first_item = items[0]
    article_title = first_item.find('title').text
    article_link = first_item.find('link').text
    
    print(f"\n[1] Targeting top LeMonde Article: {article_title}")
    print(f"[1] Link: {article_link}")
    
    # 2. FETCH CONTENT (Try top articles until one works or fallback)
    from api import extract_text_from_url, parse_text_structure
    
    text_content = None
    for idx in range(min(5, len(items))):
        item = items[idx]
        link = item.find('link').text
        title = item.find('title').text
        desc = item.find('description').text or title
        
        print(f"Trying extraction on item {idx+1}: {title}")
        extracted = extract_text_from_url(link)
        
        if extracted and len(extracted) > 200:
            text_content = extracted
            article_link = link
            break
        else:
            # Using the RSS XML tag <description> as the real payload if the site is Paywalled
            print(f"Extraction failed (Likely 402 Paywall). Using RSS Description as payload for complete pipeline.")
            text_content = f"{title}\n\n{desc}"
            article_link = link
            break

    assert text_content and len(text_content) > 30, "Failed to establish any real content from le figaro"
    
    # 3. PARSE STRUCTURE (Double Voice requirement setup) Dialogue
    dialogue, usage, _ = parse_text_structure(text_content, model="gemini-2.5-flash")
    assert dialogue and len(dialogue) > 0, "Gemini Analysis failed to create any dialog segments"
    
    outfile_name = f"pytest_dual_{int(time.time())}.wav"
    if not os.path.exists("assets"):
        os.makedirs("assets")
        
    # 4. TRIGGER SYNTHESIS (Background submission manager)
    print("[2] Submitting Multi-Speaker Audio Job...")
    job_id = manager.submit_job(
        async_dual_voice,
        dialogue,
        DEFAULT_MODEL_SYNTH,
        DEFAULT_VOICE_MAIN,
        DEFAULT_VOICE_SIDEBAR,
        True, # Strict Mode
        "Standard News Prompt", # prompt_main
        "Sidebar inserted News Prompt", # prompt_sidebar
        None, None, # Seed, Temp
        False, 0, "fr-FR", outfile_name
    )
    
    # Wait for job to complete (Timeout 5 mins)
    max_retries = 60
    while max_retries > 0:
        job = manager.get_job(job_id)
        if job["status"] == "completed":
            print("[2] Job Synthesized with success.")
            break
        if job["status"] == "error":
             pytest.fail(f"Synthesize Job Crashed with error: {job.get('error')}")
        time.sleep(5)
        max_retries -= 1
        
    assert manager.get_job(job_id)["status"] == "completed", "Job did not finish within 5 minutes"
    res = manager.get_job(job_id)["result"]
    
    # Check synthesis outputs
    outfile = res.get("outfile")
    assert outfile and os.path.exists(outfile), "Audio Wave output file is missing on local filesystem"
    
    # 5. UPLOAD AND METADATA (Trigger Remote Write)
    print("[3] Uploading outputs to Remote Storage...")
    with open(outfile, "rb") as f:
        public_wav_path = storage.save_file(f.read(), outfile)
        
    meta = {
        "timestamp": int(time.time()),
        "mode": "Pytest RSS Pipeline",
        "url": article_link,
        "extraction_method": "BS4 fallback / intelligent",
        "model_parse": "gemini-2.5-flash",
        "api_provider": "vertexai",
        "model_synth": DEFAULT_MODEL_SYNTH,
        "voice_main": DEFAULT_VOICE_MAIN,
        "voice_sidebar": DEFAULT_VOICE_SIDEBAR,
        "strict_mode": True,
        "prompts": {"system": "pytest", "tts_main": "pytest", "tts_sidebar": "pytest"},
        "audio_file": public_wav_path,
        "duration_seconds": round(res.get("duration", 0), 2),
        "dialogue": dialogue,
        "full_text": text_content,
        "seed": None, "temperature": None,
        "status": res.get("status"),
        "usage": res.get("usage")
    }
    
    # This also TRIGGERS RemoteStorage.update_rss_feed() !
    storage.save_metadata(meta, public_wav_path)
    print("\n[3] Metadata pushed and RSS generation triggered.")
    
    # 6. PULL OUTPUT RSS FEED AND VERIFY RECENT ADDITIONS
    print("[4] Downloading updated RSS output XML file (Waiting for GCS Propagation)...")
    public_rss_url = f"https://storage.googleapis.com/{storage.bucket_name}/rss.xml"
    
    matched = False
    max_rss_retries = 5
    for attempt in range(max_rss_retries):
        print(f"    -> Fetching RSS (Attempt {attempt + 1}/{max_rss_retries})")
        time.sleep(5)  # Wait 5 seconds between polls
        
        # Cache-busting parameter to invalidate CDN cache
        cache_busting_url = f"{public_rss_url}?t={int(time.time() * 1000)}"
        r_rss = requests.get(cache_busting_url, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
        
        if r_rss.status_code != 200:
            print(f"       Failed to fetch RSS. Status: {r_rss.status_code}")
            continue
            
        rss_root = ET.fromstring(r_rss.text)
        found_items = rss_root.findall('.//item')
    
        # Match title/link from point [1] with elements in output RSS items
        for rss_el in found_items:
            remote_audio_link = rss_el.find("enclosure").attrib.get("url") if rss_el.find("enclosure") is not None else ""
            if public_wav_path in remote_audio_link:
                matched = True
                break
                
        if matched:
            break
            
    assert matched, f"Workflow Incomplete: new audio file {public_wav_path} was not listed in the published output RSS feed."
    print("\n[SUCCESS] Output RSS contains the newly generated element.")
    
    # Cleanup local
    if os.path.exists(outfile):
        os.remove(outfile)
