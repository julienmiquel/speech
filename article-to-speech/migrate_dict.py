import json

dict_path = "pronunciation_dictionary.json"

try:
    with open(dict_path, "r", encoding="utf-8") as f:
        old_dict = json.load(f)
        
    new_dict = {}
    import re
    
    for k, v in old_dict.items():
        if isinstance(v, dict):
            # Already mapped
            new_dict[k] = v
        else:
            # Guessing based on previous logic 
            if re.search(r'[A-Z\-]', v):
                new_dict[k] = {"inline": v, "ipa": ""}
            else:
                new_dict[k] = {"inline": "", "ipa": v}
                
    with open(dict_path, "w", encoding="utf-8") as f:
        json.dump(new_dict, f, ensure_ascii=False, indent=4)
        
    print(f"Migrated {len(new_dict)} entries successfully.")
except Exception as e:
    print(f"Error migrating dictionary: {e}")
