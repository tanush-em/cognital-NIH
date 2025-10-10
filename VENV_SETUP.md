# Virtual Environment Setup - Complete ✅

The backend is now configured with a Python virtual environment for isolated dependency management.

## What Was Done

### 1. Created Virtual Environment
- Location: `backend/venv/`
- Python version: 3.12
- All dependencies installed from `requirements.txt`

### 2. Installed All Dependencies
Successfully installed 100+ packages including:
- **flask** (3.0.0) - Web framework
- **langchain** (0.1.0) - LLM orchestration
- **chromadb** (0.4.22) - Vector database
- **google-generativeai** (0.3.2) - Gemini API
- **pytesseract** (0.3.10) - OCR wrapper
- **Pillow** (10.1.0) - Image processing
- **PyPDF2** (3.0.1) - PDF processing
- And many more dependencies...

### 3. Created Setup Scripts
- **backend/setup.sh** - Unix/macOS/Linux setup script
- **backend/setup.bat** - Windows setup script

### 4. Updated Startup Scripts
All startup scripts now automatically:
- Check for virtual environment
- Create it if missing
- Activate it before running
- Install dependencies if needed

## Project Structure

```
backend/
├── venv/                    ✅ Virtual environment (NEW)
│   ├── bin/                 Python executables
│   ├── lib/                 Installed packages
│   └── pyvenv.cfg          Configuration
├── app.py                   Flask application
├── rag_pipeline.py          RAG implementation
├── ocr_utils.py             OCR utilities
├── requirements.txt         Python dependencies
├── setup.sh                 ✅ Setup script (NEW)
├── setup.bat                ✅ Setup script (NEW)
├── README.md                ✅ Backend documentation (NEW)
├── .env.example             Environment template
└── chroma_store/            ChromaDB storage (created at runtime)
```

## How to Use

### Option 1: Quick Start (Recommended)

```bash
# From project root
./start-backend.sh
```

The script will automatically:
1. Check if venv exists
2. Activate it
3. Check if dependencies are installed
4. Start the Flask server

### Option 2: Manual Activation

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate    # macOS/Linux
# OR
venv\Scripts\activate       # Windows

# Run the application
python app.py
```

### Option 3: First-Time Setup

If you need to recreate or setup from scratch:

```bash
cd backend
./setup.sh              # macOS/Linux
# OR
setup.bat               # Windows
```

## Verifying the Setup

### Check if venv is activated:
```bash
which python
# Should show: /Users/tanush/Documents/repos/NIH/backend/venv/bin/python
```

### Check installed packages:
```bash
pip list
# Should show all installed packages
```

### Test the backend:
```bash
python app.py
# Should start Flask server on http://localhost:5000
```

## Benefits of Virtual Environment

### ✅ Isolation
- Dependencies don't interfere with system Python
- Each project has its own package versions
- No conflicts with other projects

### ✅ Reproducibility
- Everyone uses the same package versions
- Easy to recreate on different machines
- Consistent development environment

### ✅ Clean Management
- Easy to add/remove packages
- Simple to update dependencies
- Can delete and recreate anytime

## Common Commands

### Activate Virtual Environment
```bash
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Install New Package
```bash
# With venv activated
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Reinstall All Dependencies
```bash
# With venv activated
pip install -r requirements.txt
```

### Recreate Virtual Environment
```bash
# Delete existing venv
rm -rf venv/

# Create new one
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Troubleshooting

### "Command not found: python"
Make sure the virtual environment is activated:
```bash
source venv/bin/activate
```

### "No module named 'flask'"
The virtual environment may not have packages installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Permission denied: ./setup.sh"
Make the script executable:
```bash
chmod +x setup.sh
```

### Starting Fresh
If something goes wrong, you can always delete and recreate:
```bash
cd backend
rm -rf venv/
./setup.sh
```

## Next Steps

1. **Configure API Key**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

2. **Start Backend**
   ```bash
   ./start-backend.sh
   ```

3. **Test the API**
   ```bash
   curl http://localhost:5000/health
   ```

4. **Start Frontend** (in another terminal)
   ```bash
   ./start-frontend.sh
   ```

## Files Modified/Created

### New Files
- ✅ `backend/venv/` - Virtual environment directory
- ✅ `backend/setup.sh` - Unix setup script
- ✅ `backend/setup.bat` - Windows setup script
- ✅ `backend/README.md` - Backend documentation
- ✅ `VENV_SETUP.md` - This file

### Modified Files
- ✅ `start-backend.sh` - Now checks/creates venv
- ✅ `start-backend.bat` - Now checks/creates venv
- ✅ `.gitignore` - Excludes venv directory

## Git Integration

The virtual environment is properly excluded from git:
- ✅ Added `venv/` to `.gitignore`
- ✅ Environment directory won't be committed
- ✅ Only `requirements.txt` is tracked

Other developers can recreate the exact same environment:
```bash
git clone <repo>
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Summary

✅ Virtual environment created and activated  
✅ All 100+ dependencies installed successfully  
✅ Setup scripts created for easy setup  
✅ Startup scripts updated to use venv automatically  
✅ Documentation added (backend/README.md)  
✅ Git configured to ignore venv directory  
✅ Ready to run!

---

**You're all set!** The backend now uses a proper Python virtual environment for clean, isolated dependency management.

To start developing:
```bash
./start-backend.sh        # Terminal 1
./start-frontend.sh       # Terminal 2
```

Then open: http://localhost:3000

