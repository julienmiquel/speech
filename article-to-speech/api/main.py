from fastapi import FastAPI, HTTPException, Body, BackgroundTasks, UploadFile, File, Form, Depends
from pydantic import BaseModel
from typing import Any
import time

from api.scraper import extract_text_from_url, extract_text_from_url_with_gemini
from api.parser import parse_text_structure, research_pronunciations
from api.tts import synthesize_multi_speaker, synthesize_and_save, synthesize_replicated_voice
from api.dictionary import load_pronunciation_dictionary, update_pronunciation_dictionary
from api.utils import convert_url_to_file_name, build_metadata
from job_manager import manager as job_manager
import os
from storage import LocalStorage, RemoteStorage, StorageProvider

def get_storage():
    app_mode = os.environ.get("APP_MODE", "local")
    if app_mode == "remote":
        return RemoteStorage(
            bucket_name=os.environ.get("GCS_BUCKET_NAME", "your-bucket-name"),
            project_id=os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id")
        )
    return LocalStorage(base_dir="assets")

storage_client = get_storage()

app = FastAPI(
    title="Article to Speech API",
    description="Génération audio d'articles avec parsing d'enchaînement et clonage vocal",
    version="1.0.0"
)

class ExtractRequest(BaseModel):
    url: str
    method: str = "gemini" 

class ParseRequest(BaseModel):
    text: str
    strict_mode: bool = False

class SynthesizeRequest(BaseModel):
    text: str = ""
    is_multi_speaker: bool = False
    dialogue_segments: list[dict[str, str]] | None = None 
    voice_main: str | None = None
    voice_sidebar: str | None = None
    output_filename: str | None = "output_api.wav"
    strict_mode: bool = False
    prompt_main: str = ""
    prompt_sidebar: str = ""
    seed: int | None = None
    temperature: float | None = None
    apply_dictionary: bool = True
    delay_seconds: int = 0
    language: str = "fr-FR"
    model_synth: str | None = None
    
    # Metadata pass-through for storage tracking
    mode: str | None = "API"
    url: str | None = "Unknown"
    extraction_method: str | None = "API"
    model_parse: str | None = "Unknown"

class AutomateRequest(BaseModel):
    url: str
    method: str = "gemini"
    model_parse: str | None = None
    language: str = "fr-FR"
    strict_mode: bool = False
    preset_system_prompt: str = ""

@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok", "message": "Article to Speech API is running"}

@app.get("/history")
def get_history(storage: StorageProvider = Depends(get_storage)) -> dict[str, Any]:
    return {"history": storage.list_history()}

@app.post("/extract")
def extract_endpoint(req: ExtractRequest) -> dict[str, Any]:
    if req.method == "gemini":
        text, usage, is_truncated = extract_text_from_url_with_gemini(req.url)
        return {"text": text, "usage": usage, "is_truncated": is_truncated}
    else:
        text = extract_text_from_url(req.url)
        return {"text": text}

@app.post("/parse")
def parse_endpoint(req: ParseRequest) -> dict[str, Any]:
    dialogue, usage, is_truncated = parse_text_structure(req.text, strict_mode=req.strict_mode)
    if dialogue is None:
         raise HTTPException(status_code=500, detail="Failed to parse structure")
    return {"dialogue": dialogue, "usage": usage, "is_truncated": is_truncated}

@app.get("/dictionary")
def get_dictionary() -> dict[str, Any]:
    return load_pronunciation_dictionary()

@app.post("/dictionary/update")
def update_dictionary(guides: list[dict[str, str]] = Body(...)) -> dict[str, Any]:
    added = update_pronunciation_dictionary(guides)
    return {"added_count": added, "status": "success"}

# --- Async Synthesize Endpoints (using Job Manager) ---

def run_synthesis_task(updater, req: SynthesizeRequest, storage: StorageProvider) -> dict[str, Any]:
    updater(progress=0.1, message="Starting synthesis...")
    output_filename = f"assets/{req.output_filename}"
    
    def on_progress(current, total, data=None):
        pct = 0.1 + (0.8 * (current / total))
        updater(progress=pct, message=f"Synthesizing segment {current}/{total}...")
    
    if req.is_multi_speaker:
        res, status, usage = synthesize_multi_speaker(
            dialogue=req.dialogue_segments,
            voice_main=req.voice_main,
            voice_sidebar=req.voice_sidebar,
            output_file=output_filename,
            model=req.model_synth,
            strict_mode=req.strict_mode,
            prompt_main=req.prompt_main,
            prompt_sidebar=req.prompt_sidebar,
            seed=req.seed,
            temperature=req.temperature,
            apply_dictionary=req.apply_dictionary,
            delay_seconds=req.delay_seconds,
            language=req.language,
            progress_callback=on_progress
        )
    else:
        res, status, usage = synthesize_and_save(
            text=req.text,
            voice=req.voice_main,
            output_file=output_filename,
            model=req.model_synth,
            system_instruction=req.prompt_main,
            apply_dictionary=req.apply_dictionary,
            language=req.language,
            progress_callback=on_progress
        )
        
    if not res:
        raise Exception(f"Synthesis failed: {status}")
        
    meta = build_metadata(
        outfile=output_filename,
        mode=req.mode,
        url=req.url,
        extraction_method=req.extraction_method,
        model_parse=req.model_parse,
        model_synth=req.model_synth,
        voice_main=req.voice_main,
        voice_sidebar=req.voice_sidebar,
        strict_mode=req.strict_mode,
        prompt_system="N/A",
        prompt_main=req.prompt_main,
        prompt_sidebar=req.prompt_sidebar,
        dialogue=req.dialogue_segments,
        seed=req.seed,
        temperature=req.temperature,
        apply_dict=req.apply_dictionary,
        status=status,
        usage=usage,
        duration=None,
        full_text=req.text
    )
    storage.save_metadata(meta, output_filename)
        
    updater(progress=1.0, message="Synthesis complete!")
    return {"audio_url": output_filename, "status": status, "usage": usage}

@app.post("/synthesize/async")
def synthesize_async_endpoint(req: SynthesizeRequest, storage: StorageProvider = Depends(get_storage)) -> dict[str, str]:
    job_id = job_manager.submit_job(run_synthesis_task, req, storage)
    return {"job_id": job_id, "status": "queued"}

@app.post("/synthesize/clone/async")
def synthesize_clone_endpoint(
    text: str = Form(...),
    project_id: str = Form(...),
    location: str = Form("us-central1"),
    apply_dictionary: bool = Form(True),
    language: str = Form("fr-FR"),
    output_filename: str = Form("output_cloned.wav"),
    reference_audio: UploadFile = File(...)
):
    audio_bytes = reference_audio.file.read()

    def run_clone_task(updater):
        updater(0.1, "Starting voice cloning on Vertex AI...")
        res, status, usage = synthesize_replicated_voice(
            text=text,
            reference_audio_bytes=audio_bytes,
            project_id=project_id,
            location=location,
            output_file=f"assets/{output_filename}",
            apply_dictionary=apply_dictionary,
            language=language
        )
        if not res:
            raise Exception(f"Voice cloning failed: {status}")
        updater(1.0, "Cloning complete!")
        return {"audio_url": f"assets/{output_filename}", "status": status, "usage": usage}

    job_id = job_manager.submit_job(run_clone_task)
    return {"job_id": job_id, "status": "queued"}

def run_automation_task(updater, req: AutomateRequest):
    result = {
        "text_content": None,
        "pronunciation_guides": None,
        "dialogue": None,
        "added_dict": 0,
        "total_usage": {"prompt_token_count": 0, "candidates_token_count": 0, "total_token_count": 0},
        "truncated": False
    }
    
    def add_usage(u):
        if u:
            for k in result["total_usage"]: result["total_usage"][k] += u.get(k, 0)

    updater(0.1, "1. Préparation du texte...")
    if req.method == "gemini":
        text, u, is_truncated = extract_text_from_url_with_gemini(req.url, parsing_model=req.model_parse)
        add_usage(u)
        if not text:
            text = extract_text_from_url(req.url)
        if is_truncated: result["truncated"] = True
    else:
        text = extract_text_from_url(req.url)
        
    result["text_content"] = text

    if result["text_content"]:
        updater(0.4, "2. Recherche de prononciation...")
        guides, u = research_pronunciations(result["text_content"], model=req.model_parse, language=req.language)
        add_usage(u)
        if guides:
            result["pronunciation_guides"] = guides
            added = update_pronunciation_dictionary(guides)
            result["added_dict"] = added
        
        updater(0.7, "3. Analyse de la structure...")
        dialogue, u, is_truncated = parse_text_structure(result["text_content"], model=req.model_parse, strict_mode=req.strict_mode, system_prompt=req.preset_system_prompt)
        add_usage(u)
        if is_truncated: result["truncated"] = True
        if dialogue:
            result["dialogue"] = dialogue

    updater(1.0, "Automatisation terminée !")
    return result

@app.post("/automate/async")
def automate_async_endpoint(req: AutomateRequest) -> dict[str, str]:
    job_id = job_manager.submit_job(run_automation_task, req)
    return {"job_id": job_id, "status": "queued"}

@app.get("/jobs/{job_id}")
def get_job_status(job_id: str) -> dict[str, Any]:
    job = job_manager.get_job(job_id)
    if not job:
         raise HTTPException(status_code=404, detail="Job not found")
    return job
