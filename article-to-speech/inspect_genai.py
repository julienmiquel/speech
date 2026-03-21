
import inspect
from google.genai import types

def print_type_details(cls_name, cls):
    print(f"\n--- {cls_name} ---")
    try:
        # Get signature if possible
        sig = inspect.signature(cls)
        print(f"Signature: {sig}")
    except ValueError:
        print("Signature: Not available")
        
    # List attributes/annotations
    if hasattr(cls, "__annotations__"):
        print("Annotations:")
        for k, v in cls.__annotations__.items():
            print(f"  - {k}: {v}")
    
    # Check if it's a Pydantic model or similar (has __fields__)
    if hasattr(cls, "model_fields"):
        print("Pydantic Fields:")
        for k, v in cls.model_fields.items():
            print(f"  - {k}: {v}")

print("Inspecting Google GenAI Speech Types...")

try:
    print_type_details("types.SpeechConfig", types.SpeechConfig)
except AttributeError:
    print("types.SpeechConfig not found")

try:
    print_type_details("types.VoiceConfig", types.VoiceConfig)
except AttributeError:
    print("types.VoiceConfig not found")

try:
    print_type_details("types.PrebuiltVoiceConfig", types.PrebuiltVoiceConfig)
except AttributeError:
    print("types.PrebuiltVoiceConfig not found")

try:
    print_type_details("types.GenerateContentConfig", types.GenerateContentConfig)
except AttributeError:
    print("types.GenerateContentConfig not found")
