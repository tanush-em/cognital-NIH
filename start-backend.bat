@echo off
REM Start the Flask backend server (Windows)

echo Starting AI-First Customer Support Backend...
echo.

cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
if not exist "venv\installed" (
    echo Installing dependencies...
    pip install -r requirements.txt
    type nul > venv\installed
)

REM Check if .env file exists
if not exist ".env" (
    echo .env file not found!
    echo Please create a .env file from .env.example and add your Gemini API key
    copy .env.example .env
    echo.
    echo Edit backend\.env and add your Gemini API key, then run this script again
    pause
    exit /b 1
)

REM Start the server
echo Starting Flask server on http://localhost:5000
echo.
python app.py

