import pytest
from unittest.mock import patch, MagicMock
from app import generate_music_prompt, generate_music, save_to_firebase

@pytest.fixture
def mock_gemini():
    with patch('app.client.models.generate_content') as mock_generate:
        mock_response = MagicMock()
        mock_response.text = "1980s synth-pop, 120 BPM, heavy bassline, female vocals"
        mock_generate.return_value = mock_response
        yield mock_generate

@pytest.fixture
def mock_lyria():
    with patch('app.client.interactions.create') as mock_create:
        mock_interaction = MagicMock()
        mock_output = MagicMock()
        mock_output.type = "audio"
        mock_output.data = b'base64encodedaudio'
        mock_interaction.outputs = [mock_output]
        mock_create.return_value = mock_interaction
        yield mock_create

@pytest.fixture
def mock_firebase():
    with patch('app.bucket') as mock_bucket, \
         patch('app.db') as mock_db:

        mock_blob = MagicMock()
        mock_blob.public_url = "https://example.com/audio.mp4"
        mock_bucket.blob.return_value = mock_blob

        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "test_doc_id"
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        yield mock_bucket, mock_db

def test_generate_music_prompt(mock_gemini):
    prompt = generate_music_prompt(None, "Happy sunny day")
    assert prompt == "1980s synth-pop, 120 BPM, heavy bassline, female vocals"
    mock_gemini.assert_called_once()

@patch('app.base64.b64decode')
def test_generate_music(mock_b64decode, mock_lyria):
    mock_b64decode.return_value = b'decoded_audio_bytes'
    audio_bytes = generate_music("Test prompt")

    assert audio_bytes == b'decoded_audio_bytes'
    mock_lyria.assert_called_once()

def test_save_to_firebase(mock_firebase):
    mock_bucket, mock_db = mock_firebase

    doc_id = save_to_firebase(
        prompt="Test prompt",
        audio_bytes=b"audio data",
        image_bytes=None,
        mood_text="Happy day",
        is_public=True,
        user_id="test_user"
    )

    assert doc_id == "test_doc_id"
    assert mock_bucket.blob.call_count == 1 # Only audio blob created
    mock_db.collection.return_value.document.return_value.set.assert_called_once()

    # Verify the specific fields in the set call
    call_args = mock_db.collection.return_value.document.return_value.set.call_args[0][0]
    assert call_args['is_public'] is True
    assert call_args['user_id'] == "test_user"
    assert call_args['likes_count'] == 0
    assert call_args['views_count'] == 0
    assert call_args['listens_count'] == 0
