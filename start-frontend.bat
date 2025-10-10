@echo off
REM Start the React frontend (Windows)

echo Starting AI-First Customer Support Frontend...
echo.

cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

REM Start the development server
echo Starting Vite dev server on http://localhost:3000
echo.
call npm run dev

