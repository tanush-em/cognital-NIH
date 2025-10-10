# Setup Guide - AI-First Customer Support

This guide will walk you through setting up the AI-First Customer Support chatbot from scratch.

## Step-by-Step Setup

### Step 1: Install System Dependencies

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Tesseract OCR
brew install tesseract

# Install poppler (required for pdf2image)
brew install poppler

# Verify installation
tesseract --version
```

#### Ubuntu/Debian Linux
```bash
# Update package list
sudo apt-get update

# Install Tesseract OCR
sudo apt-get install -y tesseract-ocr

# Install poppler-utils (required for pdf2image)
sudo apt-get install -y poppler-utils

# Install Python development headers
sudo apt-get install -y python3-dev python3-pip

# Verify installation
tesseract --version
```

#### Windows
1. Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. During installation, note the installation path (usually `C:\Program Files\Tesseract-OCR`)
3. Add Tesseract to your PATH or update `ocr_utils.py`:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```
4. Download and install poppler from: http://blog.alivate.com.au/poppler-windows/

### Step 2: Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (you'll need it later)

### Step 3: Clone/Download Project

```bash
# If using git
git clone <your-repo-url>
cd ai-first-support

# Or if you have the project folder
cd /path/to/ai-first-support
```

### Step 4: Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env file and add your Gemini API key
# You can use nano, vim, or any text editor:
nano .env
# Replace 'your_key_here' with your actual Gemini API key
# Save and exit (Ctrl+X, then Y, then Enter in nano)
```

### Step 5: Setup Frontend

```bash
# Open a new terminal window/tab
cd frontend

# Install Node dependencies
npm install

# (Optional) Create .env file if you need custom API URL
cp .env.example .env
```

### Step 6: Test the Setup

#### Test Backend

```bash
# In the backend directory (with venv activated)
python app.py
```

You should see:
```
Starting AI-First Customer Support Backend...
Documents in store: 0
 * Running on http://0.0.0.0:5000
```

Visit `http://localhost:5000/health` in your browser. You should see:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-10T...",
  "documents_count": 0
}
```

#### Test Frontend

```bash
# In a new terminal, navigate to frontend directory
cd frontend
npm run dev
```

You should see:
```
VITE v5.0.8  ready in XXX ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

Open `http://localhost:3000` in your browser. You should see the chatbot interface.

### Step 7: Upload Your First Document

1. Prepare a test document (PDF or image with text)
2. In the web interface, click "Choose File"
3. Select your document
4. Click "Upload and Process"
5. Wait for the success message

### Step 8: Ask Your First Question

1. Type a question about your uploaded document in the chat input
2. Press Enter or click the send button
3. Wait for the AI response
4. Click on "source(s)" to see the retrieved context

## Common Issues and Solutions

### Issue: "ModuleNotFoundError" in Python

**Solution**: Make sure you're in the virtual environment and all dependencies are installed:
```bash
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### Issue: "tesseract is not installed or it's not in your PATH"

**Solution**: 
- Verify Tesseract is installed: `tesseract --version`
- On Windows, set the path in `ocr_utils.py`
- Add Tesseract to your system PATH

### Issue: "Cannot connect to backend" in frontend

**Solution**:
- Ensure backend is running on port 5000
- Check if `http://localhost:5000/health` works
- Verify CORS is not blocking requests
- Check browser console for specific errors

### Issue: "Invalid API key" error

**Solution**:
- Verify your Gemini API key in `backend/.env`
- Ensure no extra spaces or quotes around the key
- Check if the API key is active in Google AI Studio
- Verify you have API quota remaining

### Issue: "PDF processing fails" or "Image processing fails"

**Solution**:
- Verify Tesseract is installed correctly
- Check file format is supported (PDF, JPG, PNG, BMP, TIFF)
- Try with a smaller file first
- Check file is not corrupted
- For PDFs, ensure poppler is installed (`pdf2image` dependency)

### Issue: Port 5000 or 3000 already in use

**Solution**:
- Change backend port in `app.py`: `app.run(port=5001)`
- Change frontend port in `vite.config.js`: `server: { port: 3001 }`
- Or kill the process using the port:
  ```bash
  # Find process
  lsof -i :5000  # macOS/Linux
  # Kill it
  kill -9 <PID>
  ```

## Verification Checklist

Before considering setup complete, verify:

- [ ] Backend starts without errors
- [ ] Frontend starts and loads in browser
- [ ] Health endpoint returns success
- [ ] Can upload a test document
- [ ] Document appears in uploaded files list
- [ ] Can ask a question and get a response
- [ ] Source documents are shown
- [ ] No errors in browser console
- [ ] No errors in backend terminal

## Next Steps

Once setup is complete:

1. Upload relevant documents for your use case
2. Test with various question types
3. Experiment with different document formats
4. Check the README.md for advanced configuration
5. Explore the code to understand the RAG pipeline

## Need Help?

- Check the main README.md for detailed documentation
- Review error messages carefully
- Check Python and Node.js versions
- Ensure all dependencies are installed
- Open an issue on GitHub if problems persist

---

Happy coding! 🚀

