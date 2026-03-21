import os
import sys

# Mocking environment variables for testing
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
os.environ["LOCATION"] = "us-central1"

try:
    from gemini_url_to_audio import PROMPT_ANCHOR, PROMPT_REPORTER
    
    print("Checking PROMPT_ANCHOR...")
    print(PROMPT_ANCHOR)
    assert "news" in PROMPT_ANCHOR.lower()
    
    print("\nChecking PROMPT_REPORTER...")
    print(PROMPT_REPORTER)
    assert "[surprised]" in PROMPT_REPORTER
    assert "[laughing]" in PROMPT_REPORTER
    
    print("\nVerification successful!")
except Exception as e:
    print(f"\nVerification failed: {e}")
    sys.exit(1)
