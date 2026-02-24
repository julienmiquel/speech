
import json
import os
import sys
# Add current directory to sys.path
sys.path.append(os.getcwd())

from gemini_url_to_audio import synthesize_multi_speaker
from dotenv import load_dotenv

load_dotenv()

# Mock dialogue
DIALOGUE = [
    {"speaker": "R", "text": "Testing status return.", "prompt": "Read clearly."}
]
MODEL = "gemini-2.5-flash-tts"
VOICE = "Aoede"
OUTPUT = "test_status.wav"

print(f"Generating Audio to check return signature...")
try:
    result = synthesize_multi_speaker(
        DIALOGUE, 
        model=MODEL, 
        voice_main=VOICE, 
        voice_sidebar=VOICE, 
        output_file=OUTPUT
    )
    
    if isinstance(result, tuple) and len(result) == 3:
        outfile, status, usage = result
        print(f"SUCCESS: Function returned a tuple of 3.")
        print(f"Outfile: {outfile}")
        print(f"Status: {status}")
        
        if status.get("state") == "completed":
            print("SUCCESS: Status state is 'completed'.")
            print(f"WARNING: Status state is '{status.get('state')}'.")
        
        if usage:
            print(f"SUCCESS: Usage metadata returned: {usage}")
        else:
            print("WARNING: Usage metadata is empty (expected if mock or dry run, but verify).")
            
    else:
        print(f"FAILURE: Function did NOT return a tuple. Returned: {type(result)}")
        sys.exit(1)

except Exception as e:
    print(f"FAILED: Exception caught: {e}")
    sys.exit(1)

# Clean up
if os.path.exists(OUTPUT): os.remove(OUTPUT)
