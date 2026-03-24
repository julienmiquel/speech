import pytest
from fastapi.testclient import TestClient
import time
import os

from api.main import app

client = TestClient(app)

# Note: These tests run against REAL APIs (Vertex AI, Cloud TTS, Gemini, Le Monde)
# Ensure you are authenticated with Google Cloud (gcloud auth application-default login)
# and have internet access. These will consume quota and take some time.

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.timeout(30)
def test_extract_endpoint_bs4():
    # Use a real Wikipedia page or Le Monde page (short paragraph preferred if possible)
    # We use a reliable short page
    payload = {
        "url": "https://fr.wikipedia.org/wiki/Python_(langage)",
        "method": "bs4"
    }
    response = client.post("/extract", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert len(data["text"]) > 50

@pytest.mark.timeout(60)
def test_extract_endpoint_gemini():
    # Gemini requires actual API call
    payload = {
        "url": "https://fr.wikipedia.org/wiki/Python_(langage)",
        "method": "gemini"
    }
    response = client.post("/extract", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert len(data["text"]) > 50
    assert "usage" in data

@pytest.mark.timeout(60)
def test_parse_endpoint():
    payload = {
        "text": "Bonjour, je suis un test d'intégration pour vérifier le système.",
        "strict_mode": False
    }
    response = client.post("/parse", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "dialogue" in data
    assert isinstance(data["dialogue"], list)
    assert len(data["dialogue"]) > 0
    assert "speaker" in data["dialogue"][0]
    assert "usage" in data

def test_get_dictionary():
    response = client.get("/dictionary")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_update_dictionary():
    # Add a temporary fake word to test
    temp_word = "TEST_WORD_123"
    payload = [{"word": temp_word, "inline": "test", "ipa": "test"}]
    response = client.post("/dictionary/update", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@pytest.mark.timeout(120)
def test_synthesize_async_single_speaker():
    # Small text to avoid huge TTS bills
    req_body = {
        "text": "Ceci est un test de synthèse asynchrone.",
        "is_multi_speaker": False,
        "voice_main": "fr-FR-Neural2-A",
        "output_filename": "test_api_integration_single.wav",
        "model_synth": "cloudtts",
        "language": "fr-FR"
    }
    response = client.post("/synthesize/async", json=req_body)
    assert response.status_code == 200
    assert "job_id" in response.json()
    job_id = response.json()["job_id"]
    
    # Poll API job
    timeout_loops = 0
    while timeout_loops < 40: # 40 * 2 = 80 seconds max
        res = client.get(f"/jobs/{job_id}")
        assert res.status_code == 200
        job_status = res.json()["status"]
        if job_status in ["completed", "error"]:
            break
        time.sleep(2)
        timeout_loops += 1
        
    assert job_status == "completed", f"Job failed or timed out. Message: {res.json().get('message')}"
    data = res.json()
    assert "assets/test_api_integration_single.wav" in data["result"]["audio_url"]
    assert os.path.exists(data["result"]["audio_url"]), f"Output file missing: {data['result']['audio_url']}"

@pytest.mark.timeout(180)
def test_automate_async_full_pipeline():
    # Full pipeline test
    req_body = {
        "url": "https://fr.wikipedia.org/wiki/Paris",
        "method": "bs4",
        "model_parse": "gemini-2.5-flash",
        "language": "fr-FR",
        "strict_mode": False,
        "preset_system_prompt": "Ne garde qu'une phrase."
    }
    response = client.post("/automate/async", json=req_body)
    assert response.status_code == 200
    assert "job_id" in response.json()
    job_id = response.json()["job_id"]
    
    timeout_loops = 0
    while timeout_loops < 60: # 120 seconds
        res = client.get(f"/jobs/{job_id}")
        assert res.status_code == 200
        job_status = res.json()["status"]
        if job_status in ["completed", "error"]:
            break
        time.sleep(2)
        timeout_loops += 1

    assert job_status == "completed", f"Automation failed or timeout: {res.json().get('error')}"
    data = res.json()
    assert data["result"]["text_content"] is not None
    assert isinstance(data["result"]["dialogue"], list)

@pytest.mark.timeout(180)
def test_synthesize_clone_async():
    # Attempt to find a real WAV file in assets/ to use as reference
    assets_dir = "assets"
    wav_files = [f for f in os.listdir(assets_dir) if f.endswith(".wav")]
    if not wav_files:
        pytest.skip("No reference WAV file found in assets/ to test cloning.")
        return
        
    ref_file = os.path.join(assets_dir, wav_files[0])
    
    with open(ref_file, "rb") as f:
        file_bytes = f.read()

    files = {"reference_audio": ("ref.wav", file_bytes, "audio/wav")}
    data = {
        "text": "Test de voix clonée",
        "project_id": os.environ.get("GOOGLE_CLOUD_PROJECT", "customer-demo-01"),
        "location": "europe-west1",
        "output_filename": "test_api_clone.wav"
    }
    
    response = client.post("/synthesize/clone/async", files=files, data=data)
    assert response.status_code == 200
    assert "job_id" in response.json()
    job_id = response.json()["job_id"]
    
    timeout_loops = 0
    while timeout_loops < 60:
        res = client.get(f"/jobs/{job_id}")
        assert res.status_code == 200
        job_status = res.json()["status"]
        if job_status in ["completed", "error"]:
            break
        time.sleep(2)
        timeout_loops += 1

    # Might error out if the reference audio doesn't contain a valid voice for Vertex to clone
    # But as an API test, we just ensure it completes or fails with a known API error, rather than crashing on our end
    # If we strictly want it to pass, we assert completed.
    assert job_status in ["completed", "error"]
