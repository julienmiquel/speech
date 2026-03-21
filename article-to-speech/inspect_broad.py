
import inspect
import os
from dotenv import load_dotenv
from google.genai import types

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
print(f"Loaded PROJECT_ID: {PROJECT_ID}")

def inspect_module_for_keywords(module, keywords):
    print(f"Scanning {module.__name__} for keywords: {keywords}")
    found = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) or inspect.isfunction(obj):
             if any(k.lower() in name.lower() for k in keywords):
                 found.append(name)
                 
                 # Also print details for these found items
                 print(f"\n[FOUND] {name}")
                 try:
                    sig = inspect.signature(obj)
                    print(f"  Signature: {sig}")
                 except:
                    pass
                    
                 if hasattr(obj, "model_fields"):
                    print("  Pydantic Fields:")
                    for k, v in obj.model_fields.items():
                        print(f"    - {k}: {v.description if hasattr(v, 'description') else 'No desc'}")

    return found

keywords = ["Voice", "Speech", "Audio"]
found_items = inspect_module_for_keywords(types, keywords)

print(f"\n\nTotal found: {len(found_items)}")
print(found_items)
