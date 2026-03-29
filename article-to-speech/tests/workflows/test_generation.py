import pytest
from unittest.mock import patch, MagicMock
from workflows.generation import build_metadata, enqueue_automation_followup

@patch("workflows.generation.time.time")
@patch("workflows.generation.os.environ.get")
def test_build_metadata(mock_env, mock_time):
    mock_env.return_value = "vertexai-mock"
    mock_time.return_value = 1600000000
    
    dialogue = [{"speaker": "R", "text": "Hello world"}]
    
    meta = build_metadata(
        outfile="out.wav", mode="Single", url="http", extraction_method="smart",
        model_parse="pmodel", model_synth="smodel", voice_main="v1", voice_sidebar="v2",
        strict_mode=True, prompt_system="sys", prompt_main="main", prompt_sidebar="side",
        dialogue=dialogue, seed=42, temperature=0.5, apply_dict=True,
        status={"state": "ok"}, usage={"total_token_count": 0}, duration=5.5
    )
    
    assert meta["timestamp"] == 1600000000
    assert meta["api_provider"] == "vertexai-mock"
    assert meta["audio_file"] == "out.wav"
    assert meta["duration_seconds"] == 5.5
    assert len(meta["dialogue"]) == 1
    assert meta["dialogue"][0]["original_text"] == "Hello world"
    assert meta["dialogue"][0]["text"] == "Hello world"
    
    # No dict loading check since it is not used in workflows/generation.py
    
    # Check estimated usage tokens override since total was 0
    estimated = len("Hello world") // 4
    assert meta["usage"]["total_token_count"] == estimated

@patch("workflows.generation.requests.post")
@patch("workflows.generation.MODELS_CONFIG")
@patch("workflows.generation.time.time")
def test_enqueue_automation_followup_multi(mock_time, mock_config, mock_post):
    mock_time.return_value = 1600000000
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"job_id": "JOB_123"}
    # True for multi_speaker
    mock_config.get.return_value = {"default_format": "mp3", "multi_speaker": True}
    
    mock_manager = MagicMock()
    mock_manager.submit_job.return_value = "JOB_123"
    
    res = {
        "dialogue": [{"speaker": "R", "text": "Hi"}]
    }
    job_info = {
        "auto_generate": True,
        "meta": {
            "model_synth": "test-multimodal",
            "voice_main": "v1", "voice_sidebar": "v2",
            "strict_mode": False,
            "prompts": {"tts_main": "m", "tts_sidebar": "s"},
            "seed": 0, "temperature": 1.0, "apply_dictionary": True,
            "delay_seconds": 0.5, "language": "en-US"
        }
    }
    
    job_id, info = enqueue_automation_followup(res, job_info, mock_manager)
    
    assert job_id == "JOB_123"
    assert info["type"] == "Double Voix"
    
    from unittest.mock import ANY
    mock_manager.submit_job.assert_called_once_with(ANY)

@patch("workflows.generation.requests.post")
@patch("workflows.generation.MODELS_CONFIG")
@patch("workflows.generation.time.time")
def test_enqueue_automation_followup_single(mock_time, mock_config, mock_post):
    mock_time.return_value = 1600000000
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"job_id": "JOB_456"}
    mock_config.get.return_value = {"default_format": "wav", "multi_speaker": False}
    
    mock_manager = MagicMock()
    mock_manager.submit_job.return_value = "JOB_456"
    
    res = {
        "dialogue": [{"speaker": "S", "text": "Hi"}]
    }
    job_info = {
        "auto_generate": True,
        "meta": {
            "model_synth": "test-single",
            "voice_main": "v1", "voice_sidebar": "v2",
            "strict_mode": False,
            "prompts": {"tts_main": "m", "tts_sidebar": "s"},
            "seed": 0, "temperature": 1.0, "apply_dictionary": True,
            "delay_seconds": 0.5, "language": "en-US"
        }
    }
    
    job_id, info = enqueue_automation_followup(res, job_info, mock_manager)
    
    assert job_id == "JOB_456"
    assert info["type"] == "Voix Unique"
    
    from unittest.mock import ANY
    mock_manager.submit_job.assert_called_once_with(ANY)

def test_enqueue_automation_followup_no_auto():
    assert enqueue_automation_followup({}, {"auto_generate": False}, None) is None
    assert enqueue_automation_followup({"dialogue": []}, {"auto_generate": True}, None) is None
