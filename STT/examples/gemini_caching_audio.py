import os
import sys

# Add project root to path to find STT module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from google import genai
from google.genai import types

def main():
    # Example showing how to use context caching with Gemini on Vertex AI
    PROJECT_ID = "customer-demo-01"
    REGION = "global"
    model_name = "gemini-3.5-flash"
    
    # We use a large audio file already hosted on GCS to satisfy the minimum token requirement for caching (>= 1024 tokens)
    gcs_uri = "gs://customer-demo-us-central1/stt_synthetic_tests_data/synthetic_0.wav"

    print("Initializing GenAI client for Vertex AI...")
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=REGION)

    print(f"Creating context cache for {gcs_uri}...")
    # Create the cache
    cached_content = client.caches.create(
        model=model_name,
        config=types.CreateCachedContentConfig(
            contents=[
                types.Part.from_uri(
                    file_uri=gcs_uri,
                    mime_type="audio/wav"
                )
            ],
            display_name="audio_cache_example",
            ttl="300s", # 5 minutes
        )
    )
    print(f"Created cache: {cached_content.name}")

    print("Generating content using the cache...")
    # Generate content using the cache
    response = client.models.generate_content(
        model=model_name,
        contents=["Transcribe the audio"],
        config=types.GenerateContentConfig(
            cached_content=cached_content.name
        )
    )

    print("\nTranscription Result (truncated):")
    print(response.text[:1000] + "...")

    print("\nCleaning up cache...")
    client.caches.delete(name=cached_content.name)
    print("Cleanup complete.")

if __name__ == "__main__":
    main()
