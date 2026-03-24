import os
import logging
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Config
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "customer-demo-01") 
LOCATION = os.getenv("LOCATION", "us-central1")

# Default Models & Voices
DEFAULT_MODEL_PARSE = os.getenv("MODEL_PARSE", "gemini-2.5-flash")
DEFAULT_MODEL_SYNTH = os.getenv("MODEL_SYNTH", "gemini-2.5-pro-tts")
DEFAULT_MODEL_CLONING = os.getenv("MODEL_CLONING", "gemini-2.5-flash-tts-eap-11-2025")
DEFAULT_VOICE_MAIN = os.getenv("VOICE_MAIN", "Aoede")
DEFAULT_VOICE_SIDEBAR = os.getenv("VOICE_SIDEBAR", "Fenrir")

# Cache Config
CACHE_DIR = "assets/cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Dictionary Config
DICTIONARY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pronunciation_dictionary.json")

# Vertex AI Client Initialization
try:
    vertex_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    logging.info(f"Initialized Vertex AI client for project: {PROJECT_ID}, location: {LOCATION}")
except Exception as e:
    logging.error(f"Failed to initialize client: {e}")
    vertex_client = None
