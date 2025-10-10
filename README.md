# AI-First Customer Support - RAG Chatbot

A full-stack AI-powered customer support chatbot with document upload, OCR text extraction, and RAG (Retrieval-Augmented Generation) based question answering.

## 🎯 Features

- **Document Upload**: Upload PDF and image files (JPG, PNG, BMP, TIFF)
- **OCR Text Extraction**: Automatic text extraction from images and PDFs using Tesseract
- **RAG-based QA**: Intelligent question answering using retrieved context from documents
- **Vector Storage**: Persistent embeddings storage using ChromaDB
- **Modern UI**: Beautiful Material UI interface with real-time chat
- **Source Citations**: View source documents for AI responses

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **LangChain** - LLM orchestration framework
- **Google Gemini** - LLM for text generation and embeddings
- **ChromaDB** - Vector database for embeddings
- **Tesseract OCR** - Text extraction from images
- **PyPDF2** - PDF text extraction

### Frontend
- **React.js** - UI framework
- **Vite** - Build tool
- **Material UI (MUI)** - Component library
- **Axios** - HTTP client

## 📦 Installation

### Prerequisites

1. **Python 3.8+**
2. **Node.js 16+**
3. **Tesseract OCR** - Install on your system:
   - **macOS**: `brew install tesseract`
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
4. **Google Gemini API Key** - Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_actual_api_key_here
```

### Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Create .env file (optional)
cp .env.example .env

# The default API URL is http://localhost:5000
# You can override it in .env if needed
```

## 🚀 Running the Application

### 1. Start the Backend

```bash
cd backend
python app.py
```

The backend will start on `http://localhost:5000`

### 2. Start the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

## 📖 Usage

1. **Upload Documents**
   - Click "Choose File" in the left panel
   - Select a PDF or image file
   - Click "Upload and Process"
   - Wait for the file to be processed and added to the knowledge base

2. **Ask Questions**
   - Type your question in the chat input
   - Press Enter or click the send button
   - The AI will respond based on the uploaded documents
   - Click on "source(s)" to view the retrieved context

3. **View Uploaded Files**
   - See all uploaded files in the left panel
   - View the number of chunks created from each file

## 🔌 API Endpoints

### `POST /upload`
Upload and process a document

**Request**: `multipart/form-data` with `file` field

**Response**:
```json
{
  "message": "File uploaded and processed successfully",
  "filename": "document.pdf",
  "chunks_added": 15,
  "text_length": 5432
}
```

### `POST /query`
Query the RAG system

**Request**:
```json
{
  "query": "What is the return policy?"
}
```

**Response**:
```json
{
  "answer": "According to the documentation...",
  "source_documents": [
    {
      "content": "Relevant text chunk...",
      "metadata": {
        "filename": "policy.pdf",
        "upload_date": "2025-10-10T12:00:00"
      }
    }
  ]
}
```

### `GET /documents`
List all uploaded documents

**Response**:
```json
{
  "documents": [
    {
      "filename": "document.pdf",
      "upload_date": "2025-10-10T12:00:00",
      "chunks": 15,
      "text_length": 5432
    }
  ],
  "total_count": 1,
  "total_chunks": 15
}
```

### `GET /health`
Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-10T12:00:00",
  "documents_count": 15
}
```

## ⚙️ Configuration

### Backend Configuration

Edit `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Frontend Configuration

Edit `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:5000
```

### RAG Pipeline Configuration

Edit `backend/rag_pipeline.py` to adjust:

- `CHUNK_SIZE` - Size of text chunks (default: 1000)
- `CHUNK_OVERLAP` - Overlap between chunks (default: 200)
- `CHROMA_PERSIST_DIR` - ChromaDB storage location
- Temperature and other LLM parameters

## 🐛 Troubleshooting

### Tesseract Not Found

If you get "tesseract not found" error:
- Ensure Tesseract is installed
- On macOS/Linux, verify with: `which tesseract`
- Add Tesseract to PATH if needed
- On Windows, set the path in code:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
  ```

### CORS Errors

If you see CORS errors in the browser:
- Ensure backend is running on port 5000
- Check that flask-cors is installed
- Verify the API URL in frontend matches the backend

### Gemini API Errors

If you get API errors:
- Verify your API key is correct
- Check your API quota at Google AI Studio
- Ensure you have billing enabled if required

## 📁 Project Structure

```
ai-first-support/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── ocr_utils.py          # OCR utilities
│   ├── rag_pipeline.py       # RAG implementation
│   ├── chroma_store/         # ChromaDB storage (created at runtime)
│   ├── .env                  # Environment variables (create from .env.example)
│   └── .env.example          # Environment template
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ChatWindow.jsx      # Chat interface
    │   │   ├── FileUploader.jsx    # File upload component
    │   │   └── MessageBubble.jsx   # Message display component
    │   ├── App.jsx                 # Main app component
    │   └── main.jsx                # Entry point
    ├── package.json                # Node dependencies
    ├── vite.config.js             # Vite configuration
    ├── index.html                 # HTML template
    ├── .env                       # Environment variables (optional)
    └── .env.example               # Environment template
```

## 🎨 Features in Detail

### Document Processing Pipeline

1. User uploads a file (PDF or image)
2. Backend extracts text using OCR (Tesseract for images, PyPDF2 for PDFs)
3. Text is split into chunks using LangChain's RecursiveCharacterTextSplitter
4. Each chunk is embedded using Google's embedding model
5. Embeddings are stored in ChromaDB with metadata

### RAG Query Pipeline

1. User asks a question
2. Question is embedded using the same embedding model
3. ChromaDB retrieves the most relevant chunks (semantic search)
4. Retrieved chunks are passed as context to Gemini
5. Gemini generates an answer based on the context
6. Answer and sources are returned to the user

## 🔐 Security Notes

- Never commit your `.env` file with actual API keys
- Keep your Gemini API key secure
- Consider adding authentication for production use
- Validate and sanitize all file uploads
- Set appropriate file size limits

## 📝 License

MIT License - feel free to use this project for learning and development.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 💡 Future Enhancements

- [ ] User authentication
- [ ] Multiple conversation threads
- [ ] Document deletion
- [ ] Advanced search filters
- [ ] Export chat history
- [ ] Support for more file formats (DOCX, TXT, etc.)
- [ ] Streaming responses
- [ ] Fine-tuning options
- [ ] Multi-language support

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using React, Flask, LangChain, and Google Gemini

