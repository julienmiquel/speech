import pytest
import os
from unittest.mock import MagicMock, patch
from storage import RemoteStorage, LocalStorage

@pytest.fixture
def mock_storage():
    with patch("google.cloud.storage.Client") as mock_client:
        with patch("firebase_admin.initialize_app"):
            with patch("firebase_admin.firestore.client") as mock_firestore:
                yield mock_client, mock_firestore

def test_local_storage_logic(tmp_path):
    """Test LocalStorage basic file and metadata saving."""
    base_dir = tmp_path / "assets"
    storage = LocalStorage(base_dir=str(base_dir))
    
    # Save file
    content = b"fake audio"
    dest = "test.wav"
    saved_path = storage.save_file(content, dest)
    assert os.path.exists(saved_path)
    
    # Save metadata
    meta = {"test": "data"}
    meta_path = storage.save_metadata(meta, dest)
    assert os.path.exists(meta_path)
    assert meta_path.endswith(".json")

def test_remote_storage_upload_logic(mock_storage):
    """Test RemoteStorage upload calls to GCS and Firestore."""
    mock_client, mock_firestore = mock_storage
    
    # Setup mock bucket and blob
    mock_bucket = MagicMock()
    mock_client.return_value.bucket.return_value = mock_bucket
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_blob.public_url = "https://storage.googleapis.com/bucket/test.wav"
    
    storage = RemoteStorage(bucket_name="test-bucket", project_id="test-project")
    
    # Save file
    content = b"fake audio"
    url = storage.save_file(content, "assets/test.wav")
    
    assert url == "https://storage.googleapis.com/bucket/test.wav"
    mock_blob.upload_from_string.assert_called_once()
    
    # Save metadata
    meta = {"timestamp": 123456}
    storage.save_metadata(meta, url)
    
    # Check Firestore call
    mock_firestore.return_value.collection.return_value.document.return_value.set.assert_called_once()
    called_meta = mock_firestore.return_value.collection.return_value.document.return_value.set.call_args[0][0]
    assert called_meta["timestamp"] == 123456
