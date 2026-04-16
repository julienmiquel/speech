import os
from google import genai

PROJECT_ID = "customer-demo-01" 
LOCATION = "us-central1"

if not PROJECT_ID or PROJECT_ID == "[your-project-id]":
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

print(f"Checking models for {PROJECT_ID} in {LOCATION}...")
LOCATIONS = ["us-central1", "europe-west1", "global"]
try:
    for location in LOCATIONS:
        print(f"Checking models for {PROJECT_ID} in {location}...")
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=location)
        for m in client.models.list():
            print(f"Model: {m.name} - {m.version} - {m.display_name} - {m.description}")
            
        
        

except Exception as e:
    print(f"Error listing models: {e}")
