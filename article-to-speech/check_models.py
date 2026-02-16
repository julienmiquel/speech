import os
from google import genai

PROJECT_ID = "customer-demo-01" 
LOCATION = "us-central1"

if not PROJECT_ID or PROJECT_ID == "[your-project-id]":
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

print(f"Checking models for {PROJECT_ID} in {LOCATION}...")

try:
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    for m in client.models.list(config={"page_size": 100}):
        print(f"Model: {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
