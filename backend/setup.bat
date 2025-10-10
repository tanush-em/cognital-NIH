@echo off
REM Backend Setup Script - Creates venv and installs dependencies (Windows)

echo Setting up Backend Environment...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env and add your Gemini API key!
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo Backend setup complete!
echo.
echo To activate the virtual environment:
echo   venv\Scripts\activate.bat
echo.
echo To start the backend:
echo   python app.py
echo.
echo Or use the startup script:
echo   ..\start-backend.bat
echo ========================================
pause

