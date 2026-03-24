import os
import json
import logging
import re
from google.cloud import texttospeech
from api.config import DICTIONARY_PATH

def load_pronunciation_dictionary():
    """Loads the pronunciation dictionary from a JSON file."""
    if os.path.exists(DICTIONARY_PATH):
        try:
            with open(DICTIONARY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading dictionary: {e}")
    return {}

def save_pronunciation_dictionary(dictionary):
    """Saves the pronunciation dictionary to a JSON file."""
    try:
        with open(DICTIONARY_PATH, "w", encoding="utf-8") as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logging.error(f"Error saving dictionary: {e}")
        return False

def update_pronunciation_dictionary(new_guides):
    """
    Updates the dictionary with new guides if they don't exist.
    """
    if not new_guides:
        return 0
        
    current_dict = load_pronunciation_dictionary()
    added_count = 0
    for guide in new_guides:
        term = guide.get("term")
        inline = guide.get("inline", "")
        ipa = guide.get("ipa", "")
        
        if not inline and not ipa and "guide" in guide:
            old_guide = guide["guide"]
            if re.search(r'[A-Z\-]', old_guide):
                inline = old_guide
            else:
                ipa = old_guide

        if term and (inline or ipa) and term not in current_dict:
            current_dict[term] = {
                "inline": inline,
                "ipa": ipa
            }
            added_count += 1
            
    if added_count > 0:
        save_pronunciation_dictionary(current_dict)
    return added_count

def apply_pronunciation_dictionary(text, dictionary=None):
    """Replaces words in the text based on the 'inline' pronunciation dictionary field."""
    if dictionary is None:
        dictionary = load_pronunciation_dictionary()
    
    if not dictionary:
        return text
    
    sorted_keys = sorted(dictionary.keys(), key=len, reverse=True)
    
    processed_text = text
    for word in sorted_keys:
        entry = dictionary[word]
        if isinstance(entry, dict):
            inline_val = entry.get("inline", "")
        else:
            inline_val = entry

        if inline_val:
            pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
            processed_text = pattern.sub(inline_val, processed_text)
        
    return processed_text

def prepare_tts_dictionaries(p_dict, provider_type="cloudtts"):
    """
    Processes the raw pronunciation dictionary into formats suitable for TTS providers.
    """
    pseudo_dict = {}
    ipa_params = []
    applied_ipa = {}
    
    if not p_dict:
        return {}, [], {}

    unique_phrases = set()
    for k, v in p_dict.items():
        key_lower = k.lower()
        if key_lower not in unique_phrases:
            unique_phrases.add(key_lower)
            
            if isinstance(v, dict):
                inline_val = v.get("inline", "")
                ipa_val = v.get("ipa", "")
            else:
                if re.search(r'[A-Z\-]', v):
                    inline_val = v
                    ipa_val = ""
                else:
                    inline_val = ""
                    ipa_val = v
            
            if provider_type == "cloudtts" and ipa_val:
                applied_ipa[k] = ipa_val
                ipa_params.append(
                    texttospeech.CustomPronunciationParams(
                        phrase=key_lower,
                        pronunciation=ipa_val,
                        phonetic_encoding=texttospeech.CustomPronunciationParams.PhoneticEncoding.PHONETIC_ENCODING_IPA
                    )
                )
            elif inline_val:
                pseudo_dict[k] = inline_val
                
    return pseudo_dict, ipa_params, applied_ipa
