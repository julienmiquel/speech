#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping all services..."
    kill $(jobs -p) 2>/dev/null
}
trap cleanup EXIT

# Start FastAPI backend
echo "Starting FastAPI backend..."
uvicorn api.main:app --port 8000 &

# Start Streamlit frontend
echo "Starting Streamlit frontend..."
streamlit run app.py
