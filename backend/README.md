# Backend - AI Customer Support

Flask-based backend with OCR, RAG pipeline, and vector storage.

## Setup

### Quick Setup (Recommended)

```bash
# Run the setup script
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Create .env file from template

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and add your Gemini API key
```

## Configuration

Edit `.env` file:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

## Running

### Using the startup script (from project root):

```bash
../start-backend.sh
```

### Manual start:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the server
python app.py
```

The server will start on: http://localhost:5000

## API Endpoints

### POST /upload
Upload and process documents (PDF or images)

**Request:** `multipart/form-data` with file

**Response:**
```json
{
  "message": "File uploaded and processed successfully",
  "filename": "document.pdf",
  "chunks_added": 15,
  "text_length": 5432
}
```

### POST /query
Query the RAG system

**Request:**
```json
{
  "query": "What is the return policy?"
}
```

**Response:**
```json
{
  "answer": "According to the documents...",
  "source_documents": [...]
}
```

### GET /documents
List all uploaded documents

### GET /health
Health check

## Project Structure

```
backend/
├── app.py              # Flask application (main)
├── rag_pipeline.py     # RAG implementation
├── ocr_utils.py        # OCR utilities
├── requirements.txt    # Python dependencies
├── setup.sh            # Setup script (Unix)
├── setup.bat           # Setup script (Windows)
├── .env                # Environment variables (create from .env.example)
├── .env.example        # Environment template
├── venv/               # Virtual environment (created by setup)
└── chroma_store/       # ChromaDB storage (created at runtime)
```

## Dependencies

- **Flask** - Web framework
- **LangChain** - LLM orchestration
- **ChromaDB** - Vector database
- **Google Generative AI** - Gemini LLM
- **Tesseract** - OCR (system dependency)
- **PyPDF2** - PDF processing
- **pdf2image** - PDF to image conversion

## System Requirements

- Python 3.8+
- Tesseract OCR (install separately)
- poppler (for PDF processing)

### Installing System Dependencies

**macOS:**
```bash
brew install tesseract poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

**Windows:**
Download and install from:
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Poppler: http://blog.alivate.com.au/poppler-windows/

## Development

### Activating Virtual Environment

```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Installing New Packages

```bash
# With venv activated
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Deactivating Virtual Environment

```bash
deactivate
```

## Troubleshooting

### ImportError: No module named 'flask'

Make sure the virtual environment is activated:
```bash
source venv/bin/activate
```

### Tesseract not found

Install Tesseract system dependency (see above).

On Windows, you may need to set the path in `ocr_utils.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### ChromaDB errors

Delete the `chroma_store` directory and restart:
```bash
rm -rf chroma_store/
python app.py
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |

## Notes

- The virtual environment (`venv/`) is excluded from git
- ChromaDB storage (`chroma_store/`) persists between runs
- `.env` file is excluded from git for security
- Always use the virtual environment for consistency

