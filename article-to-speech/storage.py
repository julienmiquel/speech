import os
import json
import glob
import time
from abc import ABC, abstractmethod
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials, firestore

class StorageProvider(ABC):
    @abstractmethod
    def save_file(self, content, destination):
        """Saves binary content to a destination."""
        pass

    @abstractmethod
    def save_metadata(self, metadata, destination):
        """Saves metadata (dict) to a destination."""
        pass

    @abstractmethod
    def list_history(self):
        """Returns a list of history items (dicts)."""
        pass
    
    @abstractmethod
    def get_public_url(self, path):
         """Returns a URL/path compatible with st.audio."""
         pass

    @abstractmethod
    def download_file(self, remote_path, local_destination):
        """Downloads/Copies file to local destination for processing."""
        pass

class LocalStorage(StorageProvider):
    def __init__(self, base_dir="assets"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def save_file(self, content, destination):
        # Destination is expected to be a relative path like "assets/file.wav"
        # If it's just a filename, prepend base_dir
        if not destination.startswith(self.base_dir):
            destination = os.path.join(self.base_dir, destination)
            
        with open(destination, "wb") as f:
            f.write(content)
        return destination

    def save_metadata(self, metadata, destination):
        # We save metadata as a JSON file next to the audio
        # Destination usually matches the audio filename but with .json
        if not destination.endswith(".json"):
             destination = destination.replace(".wav", ".json")
             
        if not destination.startswith(self.base_dir):
            destination = os.path.join(self.base_dir, destination)

        with open(destination, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
        return destination

    def list_history(self):
        json_files = glob.glob(os.path.join(self.base_dir, "*.json"))
        history_items = []
        for jf in json_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Handle legacy format (list of segments)
                if isinstance(data, list):
                    filename = os.path.basename(jf)
                    # Use file modification time as timestamp
                    timestamp = os.path.getmtime(jf)
                    data = {
                        "timestamp": int(timestamp),
                        "mode": "Legacy/External",
                        "model_synth": "Unknown",
                        "url": filename,
                        "voice_main": "?",
                        "voice_sidebar": "?",
                        "strict_mode": "?",
                        "audio_file": jf.replace(".json", ".wav"),
                        "dialogue": data,
                        "prompts": {}
                    }

                # Basic normalization for local files
                if "audio_file" not in data:
                    data["audio_file"] = jf.replace(".json", ".wav")
                
                # Check if audio file actually exists
                if os.path.exists(data["audio_file"]):
                    history_items.append(data)
            except Exception as e:
                print(f"Error reading {jf}: {e}")
        return history_items

    def get_public_url(self, path):
        # For local streamlit, the path is just the local file path
        return path

    def download_file(self, remote_path, local_destination):
        # For local, remote_path IS a local path (relative to base_dir or absolute)
        # We just need to make sure it exists at local_destination
        # If they are different paths, we copy. If same, we do nothing.
        
        src = remote_path
        if not os.path.exists(src):
            # Try prepending base_dir
            src = os.path.join(self.base_dir, remote_path)
        
        if os.path.abspath(src) == os.path.abspath(local_destination):
            return local_destination
            
        if os.path.exists(src):
            # Ensure dir exists
            os.makedirs(os.path.dirname(local_destination), exist_ok=True)
            import shutil
            shutil.copy2(src, local_destination)
            return local_destination
        return None

class RemoteStorage(StorageProvider):
    def __init__(self, bucket_name, project_id):
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.client = storage.Client(project=project_id)
        self.bucket = self.client.bucket(bucket_name)
        
        # Initialize Firebase
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
        self.db = firestore.client()
        self.collection = self.db.collection(os.getenv("FIRESTORE_COLLECTION", "generations"))

    def save_file(self, content, destination):
        # Destination is the blob name in GCS
        # We strip 'assets/' prefix if present to keep bucket clean
        blob_name = destination.replace("assets/", "")
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(content, content_type="audio/wav")
        return blob.public_url

    def save_metadata(self, metadata, destination):
        # Destination for metadata is Firestore document ID
        # We can use the audio filename (without extension) as ID
        # Handle if destination is a URL or path
        filename = os.path.basename(destination)
        # Handle URL encoded characters if needed or query params? 
        # Usually public_url is clean.
        
        doc_id = os.path.splitext(filename)[0]
        
        # Strip potential common prefixes if basename failed (e.g. if it's just a path)
        doc_id = doc_id.replace("assets/", "")
        
        # Ensure we don't save the binary content or large unrelated data if passed
        # Firestore expects a dict
        
        # Add a created_at timestamp if missing
        if "created_at" not in metadata:
            metadata["created_at"] = firestore.SERVER_TIMESTAMP

        self.collection.document(doc_id).set(metadata)
        return doc_id

    def list_history(self):
        docs = self.collection.order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        history_items = []
        for doc in docs:
            data = doc.to_dict()
            # Remote data should already have the public GCS URL in 'audio_file'
            # If not, we might need to reconstruct it, but we'll assume save_metadata did its job
            history_items.append(data)
        return history_items

    def get_public_url(self, path):
        # If it's already a URL, return it
        if path.startswith("http"):
            return path
        # If it's a gs:// path or relative, we might need to sign it, 
        # but for now we are using public URLs or assuming the helper returns a web-accessible link.
        # save_file returns blob.public_url which is https://storage.googleapis.com/...
        return path

    def download_file(self, remote_path, local_destination):
        """Downloads a file from GCS to local destination."""
        # If remote_path is a URL, extract blob name
        if remote_path.startswith("http"):
             # https://storage.googleapis.com/bucket-name/blob-name
             # THIS IS BRITTLE if URL format changes or if signed URL.
             # Better to rely on what we saved.
             # Our save_file returns public_url.
             parts = remote_path.split(f"https://storage.googleapis.com/{self.bucket_name}/")
             if len(parts) > 1:
                 blob_name = parts[1]
             else:
                 # Fallback: try to just use the filename if it matches logic
                 # Or maybe the remote_path IS the blob name?
                 blob_name = os.path.basename(remote_path)
        else:
            blob_name = remote_path
            
        blob = self.bucket.blob(blob_name)
        blob.download_to_filename(local_destination)
        return local_destination
