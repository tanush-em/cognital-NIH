#!/bin/bash

# AI-Powered Telecom Support Chatbot Setup Script

echo "🛠️  Setting up AI-Powered Telecom Support Chatbot..."
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p static/logs
mkdir -p chroma_db
mkdir -p resources

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
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
    echo "⚠️  Please update GROQ_API_KEY in .env file!"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Get your Groq API key from: https://console.groq.com/"
echo "2. Update GROQ_API_KEY in the .env file"
echo "3. Run: ./start.sh"
echo ""
echo "🧪 To test the API:"
echo "   python test_api.py"
echo ""
echo "📄 To test PDF OCR integration:"
echo "   python test_pdf_integration.py"
echo ""
echo "📚 For more information, see README.md"
