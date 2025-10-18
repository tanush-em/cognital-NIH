#!/bin/bash

# AI-Powered Telecom Support Chatbot Startup Script

echo "🚀 Starting AI-Powered Telecom Support Chatbot..."
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating default configuration..."
    cat > .env << 'EOF'
# AI-powered Telecom Support Chatbot Configuration
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
PORT=5000
DATABASE_URL=sqlite:///chatbot.db
GROQ_API_KEY=your-groq-api-key-here
CHROMA_PERSIST_DIRECTORY=./chroma_db
LOG_LEVEL=INFO
LOG_FILE=./static/logs/chatbot.log
ESCALATION_CONFIDENCE_THRESHOLD=0.6
ESCALATION_MESSAGE_THRESHOLD=10
CORS_ORIGINS=*
EOF
    echo "📝 Created default .env file. Please update GROQ_API_KEY!"
fi

# Check if GROQ_API_KEY is set
if grep -q "your-groq-api-key-here" .env; then
    echo "⚠️  Please set your GROQ_API_KEY in the .env file before starting the server."
    echo "   Get your API key from: https://console.groq.com/"
    exit 1
fi

# Create necessary directories
mkdir -p static/logs
mkdir -p chroma_db

# Start the application
echo "🌟 Starting Flask application..."
echo "📍 Server will be available at: http://localhost:5000"
echo "🔌 WebSocket endpoint: ws://localhost:5000/socket.io/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================"

python app.py
