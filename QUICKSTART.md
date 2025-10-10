# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **Node.js 16+** - [Download](https://nodejs.org/)
3. **Tesseract OCR** - Installation:
   - **macOS**: `brew install tesseract poppler`
   - **Ubuntu**: `sudo apt-get install tesseract-ocr poppler-utils`
   - **Windows**: [Download Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
4. **Gemini API Key** - [Get it here](https://makersuite.google.com/app/apikey)

## Setup (First Time Only)

### 1. Configure Backend

```bash
cd backend
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 2. Install Backend Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install packages
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Running the Application

### Option 1: Using Startup Scripts (Easiest)

#### macOS/Linux
```bash
# Terminal 1 - Backend
./start-backend.sh

# Terminal 2 - Frontend
./start-frontend.sh
```

#### Windows
```cmd
REM Terminal 1 - Backend
start-backend.bat

REM Terminal 2 - Frontend
start-frontend.bat
```

### Option 2: Manual Start

#### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## Access the Application

Open your browser and go to: **http://localhost:3000**

Backend API: **http://localhost:5000**

## First Steps

1. **Upload a Document**
   - Click "Choose File" in the left panel
   - Select a PDF or image file
   - Click "Upload and Process"
   - Wait for confirmation

2. **Ask Questions**
   - Type a question about your document
   - Press Enter
   - View the AI response and sources

## Quick Test

Try this sample workflow:

1. Upload a PDF (any document with text)
2. Ask: "What is this document about?"
3. Ask: "Summarize the main points"
4. Click on "source(s)" to see retrieved context

## Troubleshooting

### Backend won't start
- Check if Tesseract is installed: `tesseract --version`
- Verify your Gemini API key in `backend/.env`
- Ensure Python virtual environment is activated

### Frontend won't connect
- Confirm backend is running on port 5000
- Check `http://localhost:5000/health` returns success
- Clear browser cache

### File upload fails
- Check file format (PDF, JPG, PNG, BMP, TIFF)
- Ensure file is under 10MB
- Verify Tesseract is properly installed

## Need More Help?

- See **README.md** for full documentation
- See **SETUP_GUIDE.md** for detailed setup
- Check logs in terminal for error messages

---

**That's it! You're ready to go! 🎉**

