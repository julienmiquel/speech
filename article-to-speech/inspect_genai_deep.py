
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
    
print("Inspecting Google GenAI Speech Types (Deep Dive)...")

try:
    print_type_details("types.MultiSpeakerVoiceConfig", types.MultiSpeakerVoiceConfig)
except AttributeError:
    print("types.MultiSpeakerVoiceConfig not found")

try:
    print_type_details("types.ReplicatedVoiceConfig", types.ReplicatedVoiceConfig)
except AttributeError:
    print("types.ReplicatedVoiceConfig not found")
