# Changelog

All notable changes to the AI-First Customer Support project.

## [1.0.0] - 2025-10-10

### 🎉 Initial Release

Complete MVP implementation of RAG-based customer support chatbot.

### ✨ Features

#### Backend
- **Flask REST API** with CORS support
  - POST /upload - Document upload and processing
  - POST /query - RAG-based question answering
  - GET /documents - List uploaded documents
  - GET /health - Health check endpoint

- **OCR Processing**
  - PDF text extraction using PyPDF2
  - Image text extraction using Tesseract OCR
  - Fallback OCR for scanned PDFs
  - Support for PDF, JPG, PNG, BMP, TIFF formats

- **RAG Pipeline**
  - LangChain integration
  - Google Gemini for embeddings and generation
  - ChromaDB vector storage
  - Configurable text chunking (1000 chars, 200 overlap)
  - Source document citations

#### Frontend
- **Modern React UI** with Material-UI
  - Responsive design
  - Real-time chat interface
  - File upload with drag-and-drop support
  - Document list viewer
  - Source citation accordion

- **Components**
  - App.jsx - Main application container
  - ChatWindow.jsx - Chat interface
  - MessageBubble.jsx - Message display
  - FileUploader.jsx - File upload component

#### Documentation
- README.md - Complete project documentation
- QUICKSTART.md - 5-minute setup guide
- SETUP_GUIDE.md - Detailed setup instructions
- ARCHITECTURE.md - System architecture overview
- PROJECT_SUMMARY.md - Project overview
- CHANGELOG.md - This file

#### Automation
- start-backend.sh/bat - Backend startup scripts
- start-frontend.sh/bat - Frontend startup scripts
- verify-setup.sh - Setup verification script

### 🔧 Configuration
- Environment-based API key management
- Configurable chunk size and overlap
- Adjustable retrieval parameters
- Temperature control for LLM

### 🔒 Security
- File type validation
- File size limits (10MB)
- Input sanitization
- Environment variable protection
- CORS configuration

### 📦 Dependencies

#### Backend
- flask==3.0.0
- flask-cors==4.0.0
- langchain==0.1.0
- langchain-google-genai==0.0.6
- chromadb==0.4.22
- python-dotenv==1.0.0
- pytesseract==0.3.10
- Pillow==10.1.0
- PyPDF2==3.0.1
- pdf2image==1.16.3

#### Frontend
- react==18.2.0
- react-dom==18.2.0
- @mui/material==5.15.0
- @mui/icons-material==5.15.0
- @emotion/react==11.11.3
- @emotion/styled==11.11.0
- axios==1.6.2
- vite==5.0.8

### 📝 Known Limitations
- Single user, no authentication
- Local storage only (ChromaDB)
- Synchronous processing
- No response streaming
- Memory-based file metadata

### 🎯 Future Enhancements
See PROJECT_SUMMARY.md for detailed roadmap

---

## Version History

- **1.0.0** (2025-10-10) - Initial MVP release

---

For detailed information about the project, see README.md
For setup instructions, see QUICKSTART.md or SETUP_GUIDE.md

