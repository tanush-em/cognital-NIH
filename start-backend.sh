#!/bin/bash
# Start the Flask backend server

echo "🚀 Starting AI-First Customer Support Backend..."
echo ""

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    touch venv/installed
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Please create a .env file from .env.example and add your Gemini API key"
    cp .env.example .env
    echo ""
    echo "Edit backend/.env and add your Gemini API key, then run this script again"
    exit 1
fi

# Start the server
echo "✅ Starting Flask server on http://localhost:5000"
echo ""
python app.py

