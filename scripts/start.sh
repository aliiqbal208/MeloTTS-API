#!/bin/bash

# MeloTTS API Server Startup Script

set -e

echo "🚀 Starting MeloTTS API Server..."

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "📦 Running in Docker container"
    # Models should already be downloaded during build
else
    echo "💻 Running locally - checking dependencies..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Download models if not present
    if [ ! -d "MeloTTS/models" ]; then
        echo "📥 Downloading MeloTTS models..."
        python MeloTTS/melo/init_downloads.py
    fi
fi

# Set environment variables
export PORT=${PORT:-8080}
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}

echo "🌐 Starting server on port $PORT"
echo "🔧 CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"

# Start the server
exec uvicorn main:app --host 0.0.0.0 --port $PORT --reload
