#!/bin/bash
# Setup Verification Script
# Run this to check if your environment is ready

echo "🔍 Verifying AI-First Customer Support Setup..."
echo ""

ERRORS=0

# Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION found"
else
    echo "   ❌ Python 3 not found"
    ERRORS=$((ERRORS + 1))
fi

# Check Node.js
echo "2. Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "   ✅ Node.js $NODE_VERSION found"
else
    echo "   ❌ Node.js not found"
    ERRORS=$((ERRORS + 1))
fi

# Check npm
echo "3. Checking npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "   ✅ npm $NPM_VERSION found"
else
    echo "   ❌ npm not found"
    ERRORS=$((ERRORS + 1))
fi

# Check Tesseract
echo "4. Checking Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n 1)
    echo "   ✅ $TESSERACT_VERSION found"
else
    echo "   ❌ Tesseract not found"
    echo "      Install: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)"
    ERRORS=$((ERRORS + 1))
fi

# Check poppler (for pdf2image)
echo "5. Checking poppler..."
if command -v pdftoppm &> /dev/null; then
    echo "   ✅ poppler found"
else
    echo "   ⚠️  poppler not found (required for PDF processing)"
    echo "      Install: brew install poppler (macOS) or apt-get install poppler-utils (Linux)"
    ERRORS=$((ERRORS + 1))
fi

# Check backend structure
echo "6. Checking backend files..."
if [ -f "backend/app.py" ] && [ -f "backend/rag_pipeline.py" ] && [ -f "backend/ocr_utils.py" ]; then
    echo "   ✅ Backend files present"
else
    echo "   ❌ Backend files missing"
    ERRORS=$((ERRORS + 1))
fi

# Check frontend structure
echo "7. Checking frontend files..."
if [ -f "frontend/package.json" ] && [ -f "frontend/src/App.jsx" ]; then
    echo "   ✅ Frontend files present"
else
    echo "   ❌ Frontend files missing"
    ERRORS=$((ERRORS + 1))
fi

# Check backend dependencies
echo "8. Checking backend dependencies..."
if [ -f "backend/requirements.txt" ]; then
    echo "   ✅ requirements.txt found"
    if [ -d "backend/venv" ]; then
        echo "   ✅ Virtual environment exists"
    else
        echo "   ⚠️  Virtual environment not created yet"
        echo "      Run: cd backend && python3 -m venv venv"
    fi
else
    echo "   ❌ requirements.txt missing"
    ERRORS=$((ERRORS + 1))
fi

# Check frontend dependencies
echo "9. Checking frontend dependencies..."
if [ -d "frontend/node_modules" ]; then
    echo "   ✅ Node modules installed"
else
    echo "   ⚠️  Node modules not installed yet"
    echo "      Run: cd frontend && npm install"
fi

# Check environment files
echo "10. Checking environment configuration..."
if [ -f "backend/.env" ]; then
    echo "   ✅ backend/.env exists"
    if grep -q "your_gemini_api_key_here" backend/.env 2>/dev/null; then
        echo "   ⚠️  Please update backend/.env with your actual Gemini API key"
    elif grep -q "your_key_here" backend/.env 2>/dev/null; then
        echo "   ⚠️  Please update backend/.env with your actual Gemini API key"
    else
        echo "   ✅ API key appears to be set"
    fi
else
    echo "   ⚠️  backend/.env not created yet"
    echo "      Run: cp backend/.env.example backend/.env"
    echo "      Then edit backend/.env to add your Gemini API key"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed! Your setup looks good."
    echo ""
    echo "Next steps:"
    echo "1. Make sure backend/.env has your Gemini API key"
    echo "2. Run: ./start-backend.sh (in one terminal)"
    echo "3. Run: ./start-frontend.sh (in another terminal)"
    echo "4. Open: http://localhost:3000"
else
    echo "⚠️  Found $ERRORS issue(s) that need attention."
    echo ""
    echo "Please fix the issues above and run this script again."
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

