#!/bin/bash

# GCP Deployment Script for Article-to-Speech

# Load environment variables from .env
if [ -f .env ]; then
    while IFS='=' read -r name value || [ -n "$name" ]; do
        # Skip comments and empty lines
        if [[ ! "$name" =~ ^# && -n "$name" ]]; then
            # Remove leading/trailing whitespace and quotes from value
            value=$(echo "$value" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
            export "$name=$value"
        fi
    done < .env
else
    echo "Error: .env file not found."
    exit 1
fi

# Configuration from .env
PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
BUCKET_NAME=${GCS_BUCKET_NAME}
REGION=${LOCATION:-europe-west9}
SERVICE_NAME="article-to-speech"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Validate required variables
if [ -z "$PROJECT_ID" ]; then
    echo "Error: GOOGLE_CLOUD_PROJECT is not set in .env"
    exit 1
fi

if [ -z "$BUCKET_NAME" ]; then
    echo "Error: GCS_BUCKET_NAME is not set in .env"
    exit 1
fi

echo "--- Deploying to GCP ---"
echo "Project ID: $PROJECT_ID"
echo "Region:     $REGION"
echo "Service:    $SERVICE_NAME"
echo "Bucket:     $BUCKET_NAME"
echo "------------------------"

# 1. Enable APIs
echo "Enabling necessary APIs..."
gcloud services enable run.googleapis.com \
                       containerregistry.googleapis.com \
                       cloudbuild.googleapis.com \
                       firestore.googleapis.com \
                       storage.googleapis.com \
                       --project "$PROJECT_ID"

# 2. Build and Push Image using Cloud Build (no local Docker required)
echo "Building and pushing container image..."
gcloud builds submit --tag "$IMAGE_NAME" --project "$PROJECT_ID"

# 3. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_NAME" \
    --platform managed \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --allow-unauthenticated \
    --set-env-vars "APP_MODE=remote,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCS_BUCKET_NAME=$BUCKET_NAME,LOCATION=$REGION,FIRESTORE_COLLECTION=${FIRESTORE_COLLECTION:-generations}"

echo "Deployment complete!"
gcloud run services describe "$SERVICE_NAME" --platform managed --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)'
