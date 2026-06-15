import os
import sys

# Add project root to path to find STT module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from google import genai
from google.genai import types

def main():
    # Example showing how to use context caching with Gemini
    # Context Caching for audio requires using the Gemini Developer API.
    # Set the GOOGLE_API_KEY environment variable.
    model_name = "gemini-1.5-pro-002" # context caching works with 1.5 models typically

    print("Initializing GenAI client for Developer API...")
    # It requires the API Key
    client = genai.Client()

    audio_file = "assets/batch/0-temp.wav"

    if not os.path.exists(audio_file):
        print(f"File {audio_file} not found. Please provide a valid audio file.")
        return

    print(f"Uploading {audio_file}...")
    # Upload the file
    uploaded_file = client.files.upload(file=audio_file)
    print(f"Uploaded file: {uploaded_file.name}")

    print("Creating context cache...")
    # Create the cache
    cached_content = client.caches.create(
        model=model_name,
        config=types.CreateCachedContentConfig(
            contents=[uploaded_file],
            display_name="audio_cache",
            ttl="3600s", # 1 hour
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

    print("\nTranscription Result:")
    print(response.text)

    print("\nCleaning up cache and file...")
    client.caches.delete(name=cached_content.name)
    client.files.delete(name=uploaded_file.name)
    print("Cleanup complete.")

if __name__ == "__main__":
    main()
