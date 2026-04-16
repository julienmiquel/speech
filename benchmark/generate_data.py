import subprocess
import os
import sys
from gtts import gTTS
from pydub import AudioSegment
from google.cloud import storage

BUCKET_NAME = "customer-demo-us-central1"

def generate_data_if_needed(n=10, force=False):
    # Check if files exist on the main test bucket
    cmd = ["gsutil", "ls", "gs://customer-demo-us-central1/stt_synthetic_tests_data/*.wav"]
    try:
        output = subprocess.check_output(cmd).decode("utf-8")
        files = [line.strip() for line in output.split("\n") if line.strip()]
        if files and not force:
            print(f"Found {len(files)} files on GCS. Skipping generation.")
            return files
    except subprocess.CalledProcessError:
        print("Failed to list files or no files found on GCS.")
        pass

    print(f"Generating {n} synthetic data items from RSS...")
    
    # Add article-to-speech to path to import its modules
    ats_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../article-to-speech'))
    sys.path.append(ats_path)
    
    from api.tts import synthesize_and_save
    from api.scraper import extract_text_from_url
    from workflows.extraction import fetch_rss_feed
    
    # Fetch articles from RSS
    items = fetch_rss_feed("https://www.lefigaro.fr/rss/figaro_actualites.xml")[:n]
    
    generated_wavs = []
    for i, item in enumerate(items):
        url = item.get("link")
        if "en-direct" in url:
            print(f"Skipping live feed: {url}")
            continue
        print(f"Processing {url}")
        try:
            text = extract_text_from_url(url)
            if not text:
                continue
                
            local_wav = f"assets/batch/synthetic_{i}.wav"
            local_txt = f"assets/batch/synthetic_{i}.txt"
            os.makedirs(os.path.dirname(local_wav), exist_ok=True)
            
            # Save ground truth
            with open(local_txt, "w", encoding="utf-8") as f:
                f.write(text)
                
            # Synthesize audio
            res, status, usage = synthesize_and_save(
                text=text,
                output_file=local_wav,
            )
            
            if res:
                # Upload to user's bucket using Python client
                storage_client = storage.Client()
                bucket = storage_client.bucket(BUCKET_NAME)
                
                gcs_wav_path = f"stt_synthetic_tests_data/synthetic_{i}.wav"
                gcs_txt_path = f"stt_synthetic_tests_data/synthetic_{i}.txt"
                
                blob_wav = bucket.blob(gcs_wav_path)
                blob_wav.upload_from_filename(local_wav)
                
                blob_txt = bucket.blob(gcs_txt_path)
                blob_txt.upload_from_filename(local_txt)
                
                gcs_wav = f"gs://{BUCKET_NAME}/{gcs_wav_path}"
                generated_wavs.append(gcs_wav)
                print(f"Uploaded {gcs_wav}")
        except Exception as e:
            print(f"Error generating data for {url}: {e}")
            
    return generated_wavs

# Keep gTTS generation
def generate_gtts_data():
    print("Generating gTTS test data...")
    os.makedirs("stt_synthetic_tests_data", exist_ok=True)

    tests = [
        ("gtts_test1", "Bonjour, ceci est un test de transcription."),
        ("gtts_test2", "Les performances des modèles sont importantes pour nous."),
        ("gtts_test3", "L'intelligence artificielle progresse rapidement.")
    ]

    for name, text in tests:
        # Generate mp3
        tts = gTTS(text=text, lang='fr')
        mp3_path = f"stt_synthetic_tests_data/{name}.mp3"
        tts.save(mp3_path)
        
        # Convert to wav
        sound = AudioSegment.from_mp3(mp3_path)
        wav_path = f"stt_synthetic_tests_data/{name}.wav"
        sound.export(wav_path, format="wav")
        
        # Remove mp3
        os.remove(mp3_path)
        
        # Save ground truth text
        with open(f"stt_synthetic_tests_data/{name}.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        print(f"Generated {wav_path} and corresponding text.")
        
        # Upload to user's bucket using Python client
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        
        gcs_wav_path = f"stt_synthetic_tests_data/{name}.wav"
        gcs_txt_path = f"stt_synthetic_tests_data/{name}.txt"
        
        blob_wav = bucket.blob(gcs_wav_path)
        blob_wav.upload_from_filename(wav_path)
        
        blob_txt = bucket.blob(gcs_txt_path)
        blob_txt.upload_from_filename(f"stt_synthetic_tests_data/{name}.txt")
        
        gcs_wav = f"gs://{BUCKET_NAME}/{gcs_wav_path}"
        print(f"Uploaded {gcs_wav}")

# Run both
wav_files = generate_data_if_needed(10, force=True)
#generate_gtts_data()
