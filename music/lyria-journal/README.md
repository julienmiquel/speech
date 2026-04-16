# Lyria Journal 🎵

Lyria Journal is an AI-based social and music application (Streamlit). It allows users to capture their "daily mood" via a photo or text, generates a detailed music prompt using **Gemini 2.5 Flash**, and then uses the **Lyria 3** API to compose a music preview (30-second clip). Creations can be kept in a private gallery or published for the community.

## Main Features
- **Photo to Music**: Take a photo to generate the music of the moment.
- **Lyria Prompting Best Practices**: Uses strict instructions for Gemini to orchestrate generation via Lyria.
- **Galleries**: Firebase storage to manage private and public galleries.

## Local Installation

1. Ensure you have Python 3.11+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your environment variables (if not using GCP by default):
   ```bash
   export GOOGLE_API_KEY="your-gemini-key"
   export GOOGLE_CLOUD_PROJECT="your-gcp-project"
   export FIREBASE_STORAGE_BUCKET="your-bucket.appspot.com"
   ```
4. Launch the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## Firebase Configuration (Prerequisites)

For storing audio tracks and metadata, this project relies on:
- **Firebase Cloud Storage** for `.mp4` audios and images.
- **Cloud Firestore** for data (prompts, dates, etc.).

You must have initialized Firebase and Firestore in your Google Cloud project.

**Important Notes for Firebase:**
1. **Firestore Indexes:** The application performs sorted queries on Firestore (e.g., `where('is_public', '==', True).order_by('created_at', descending=True)`). During the first execution of these queries, Firestore will return an error containing a direct link to create the necessary composite index. Click this link to generate the index.
2. **Storage Permissions:** For audio files to be readable by everyone, ensure your Cloud Storage bucket allows public read access (role `Storage Object Viewer` assigned to `allUsers`).

## Deployment to Cloud Run

You can deploy this application directly to Cloud Run using the provided script. It will use `gcloud run deploy` with sources from the current directory.

1. Log in to GCP:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
2. Launch the deployment:
   ```bash
   ./deploy.sh
   ```

## Tests

To run unit tests:
```bash
PYTHONPATH=. pytest tests/
```
