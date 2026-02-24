import sys
import os
import argparse
from gemini_url_to_audio import extract_text_from_url, parse_text_structure, synthesize_multi_speaker, synthesize_and_save, convert_url_to_file_name
from google import genai
from google.genai import types

# Placeholder for gTTS if we use it for comparison
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

def run_single_voice_demo(url, output_file, strict_mode=True, tts_model="gemini-2.5-pro-tts", voice_main="Aoede", voice_sidebar="Fenrir", parse_model="gemini-2.5-flash" ):
    print(f"--- Running Single Voice Demo (Strict Mode: {strict_mode}) ---")
    text = extract_text_from_url(url)
    if not text:
        print("Failed to extract text.")
        return

    print(f"Extracted {len(text)} chars.")
    
    # For single voice, we can just use synthesize_and_save but we might want strict validation?
    # Actually, synthesize_and_save doesn't have the strict prompt logic yet.
    # We should probably use `parse_text_structure` even for single voice if we want to enforce strictness via the prompt structure we added?
    # Or just use a simple prompt.
    
    # If strict mode is requested for single voice, we need to ensure the prompt says "READ EXACTLY".
    # The current `synthesize_and_save` uses "Please read this text out loud naturally:".
    # We should probably update `synthesize_and_save` or just use `synthesize_multi_speaker` with one speaker.
    # Let's use `synthesize_multi_speaker` with a single speaker "Reader" to reuse the strict logic if needed,
    # OR just update `synthesize_and_save` in the main lib. 
    # For now, let's use `synthesize_multi_speaker` as it's more robust with the structure parsing we just added.
    
    # Actually, if we want single voice, we might not want to parse structure (or maybe we do to handle ads/menus?).
    # Yes, parsing structure is good to remove garbage.
    
    dialogue, _ = parse_text_structure(text, strict_mode=strict_mode, model=parse_model)
    if not dialogue:
        print("Failed to parse structure.")
        return

    # Force all to be same speaker for single voice
    for seg in dialogue:
        seg["speaker"] = "R"
        
    synthesize_multi_speaker(
        dialogue, 
        model=tts_model, 
        voice_main=voice_main, 
        voice_sidebar=voice_sidebar, # Same voice
        output_file=output_file,
        strict_mode=strict_mode
    )

def run_dual_voice_demo(url, output_file, strict_mode=True, tts_model="gemini-2.5-pro-tts", voice_main="Aoede", voice_sidebar="Fenrir", parse_model="gemini-2.5-flash" ):
    print(f"--- Running Dual Voice Demo (Strict Mode: {strict_mode}) ---")
    text = extract_text_from_url(url)
    if not text: return

    dialogue, _ = parse_text_structure(text, strict_mode=strict_mode, model=parse_model)
    if not dialogue: return

    synthesize_multi_speaker(
        dialogue, 
        model=tts_model, 
        voice_main=voice_main, 
        voice_sidebar=voice_sidebar, 
        output_file=output_file,
        strict_mode=strict_mode
    )

def run_comparison_demo(url, output_file):
    print("--- Running Comparison Demo (Standard TTS) ---")
    if not gTTS:
        print("gTTS not installed. Skipping comparison.")
        return

    text = extract_text_from_url(url)
    if not text: return
    
    # Basic cleanup for gTTS (it reads everything)
    # We might want to use the parsed text to be fair? 
    # No, let's use the raw extraction to show the difference in "understanding" content vs garbage.
    # OR use the parsed text to compare just the Voice Quality.
    # The user manual says "Comparatif qualitatif vs. voix robotiques standard."
    # Usually implies Voice Quality. So let's use the cleaned/parsed text to be fair.
    
    dialogue, _ = parse_text_structure(text, strict_mode=True) # Use strict parsing to get clean text
    if not dialogue: return
    
    clean_text = " ".join(seg["text"] for seg in dialogue)
    
    print(f"Synthesizing {len(clean_text)} chars with gTTS...")
    tts = gTTS(text=clean_text, lang='fr')
    tts.save(output_file)
    print(f"Saved {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="News Audio Workshop - Gemini TTS Demo")
    parser.add_argument("url", help="URL of the article")
    parser.add_argument("--mode", choices=['single', 'dual', 'compare', 'all'], default='all')
    parser.add_argument("--output_dir", default="./assets")
    
    args = parser.parse_args()
    
    base_name = convert_url_to_file_name(args.url)
    
    if args.mode in ['single', 'all']:
        run_single_voice_demo(args.url, os.path.join(args.output_dir, f"{base_name}_single.wav"))
        
    if args.mode in ['dual', 'all']:
        run_dual_voice_demo(args.url, os.path.join(args.output_dir, f"{base_name}_dual.wav"))
        
    if args.mode in ['compare', 'all']:
        run_comparison_demo(args.url, os.path.join(args.output_dir, f"{base_name}_standard.wav"))
