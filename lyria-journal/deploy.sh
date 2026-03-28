#!/bin/bash

# Configuration
SERVICE_NAME="lyria-journal"
REGION="europe-west1" # Change as needed
PROJECT_ID=$(gcloud config get-value project)

# Check if Project ID is set
if [ -z "$PROJECT_ID" ]; then
  echo "Error: Google Cloud Project ID not set. Run 'gcloud config set project YOUR_PROJECT_ID'."
  exit 1
fi

echo "Deploying $SERVICE_NAME to project $PROJECT_ID in region $REGION..."

# Deploy to Cloud Run from source
gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_REGION=$REGION,FIREBASE_STORAGE_BUCKET=customer-demo-eu-pub

echo "Deployment complete."
