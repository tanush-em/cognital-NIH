# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                   (React + Vite + MUI)                      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ FileUploader │  │  ChatWindow  │  │MessageBubble │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│                      http://localhost:3000                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         Backend                             │
│                         (Flask)                             │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │     app.py   │  │ ocr_utils.py │  │rag_pipeline  │    │
│  │              │  │              │  │      .py     │    │
│  │  /upload     │──│  Tesseract   │  │              │    │
│  │  /query      │  │  PyPDF2      │  │  LangChain   │    │
│  │  /documents  │  │  pdf2image   │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                              │              │
│                      http://localhost:5000   │              │
└──────────────────────────────────────────────┼──────────────┘
                                               │
                                               ▼
                    ┌────────────────────────────────────┐
                    │        ChromaDB                    │
                    │    (Vector Database)               │
                    │                                    │
                    │  - Document Embeddings             │
                    │  - Metadata Storage                │
                    │  - Similarity Search               │
                    │                                    │
                    │  Persisted to: ./chroma_store/     │
                    └────────────────────────────────────┘
                                               │
                                               │
                                               ▼
                    ┌────────────────────────────────────┐
                    │      Google Gemini API             │
                    │                                    │
                    │  - Text Generation (gemini-pro)    │
                    │  - Embeddings (embedding-001)      │
                    └────────────────────────────────────┘
```

## Data Flow

### Document Upload Flow

```
User → FileUploader → /upload API
                         │
                         ├─→ Extract file bytes
                         │
                         ├─→ OCR Utils
                         │    ├─ PDF? → PyPDF2 (text extraction)
                         │    │         └─ No text? → pdf2image + Tesseract
                         │    └─ Image? → Tesseract OCR
                         │
                         ├─→ Text Splitting (LangChain)
                         │    └─ RecursiveCharacterTextSplitter
                         │       (chunk_size=1000, overlap=200)
                         │
                         ├─→ Generate Embeddings (Gemini)
                         │    └─ models/embedding-001
                         │
                         └─→ Store in ChromaDB
                              └─ With metadata (filename, date)
```

### Query Flow

```
User → ChatWindow → /query API
                       │
                       ├─→ Embed Query (Gemini)
                       │    └─ models/embedding-001
                       │
                       ├─→ Similarity Search (ChromaDB)
                       │    └─ Retrieve top K chunks (k=4)
                       │
                       ├─→ Create Context from Chunks
                       │
                       ├─→ Generate Answer (Gemini)
                       │    └─ gemini-pro with context
                       │    └─ Temperature: 0.3
                       │
                       └─→ Return Answer + Source Docs
                            │
                            └─→ Display in MessageBubble
```

## Component Details

### Frontend Components

#### App.jsx
- **Purpose**: Main application container
- **State Management**:
  - `messages`: Chat message history
  - `uploadedFiles`: List of uploaded documents
  - `documentCount`: Total chunks in vector DB
- **API Integration**:
  - Axios for HTTP requests
  - Error handling and notifications

#### ChatWindow.jsx
- **Purpose**: Chat interface
- **Features**:
  - Message display area with auto-scroll
  - Text input with send button
  - Enter key support
  - Loading states

#### MessageBubble.jsx
- **Purpose**: Individual message display
- **Features**:
  - User vs AI styling
  - Timestamp display
  - Source document accordion
  - Error state handling

#### FileUploader.jsx
- **Purpose**: Document upload interface
- **Features**:
  - File selection
  - Type validation (PDF, images)
  - Size validation (max 10MB)
  - Upload progress
  - Success/error feedback

### Backend Modules

#### app.py
- **Purpose**: Flask web server
- **Endpoints**:
  - `GET /health`: Health check
  - `POST /upload`: Document upload
  - `POST /query`: Question answering
  - `GET /documents`: List documents
- **Features**:
  - CORS enabled
  - Error handling
  - File metadata tracking

#### ocr_utils.py
- **Purpose**: Text extraction from documents
- **Functions**:
  - `extract_text_from_image()`: Image OCR via Tesseract
  - `extract_text_from_pdf()`: PDF text extraction
  - `extract_text()`: Unified interface
- **Fallback**: PDF OCR if text extraction fails

#### rag_pipeline.py
- **Purpose**: RAG implementation with LangChain
- **Key Components**:
  - `GoogleGenerativeAIEmbeddings`: Embedding generation
  - `Chroma`: Vector store
  - `RecursiveCharacterTextSplitter`: Text chunking
  - `RetrievalQA`: Question answering chain
- **Functions**:
  - `add_document_to_store()`: Index documents
  - `query_documents()`: RAG query
  - `get_document_count()`: Stats

## Technology Stack Details

### Frontend Stack
- **React 18**: Component-based UI
- **Vite**: Fast build tool and dev server
- **Material-UI 5**: Component library
  - `@mui/material`: Core components
  - `@mui/icons-material`: Icons
  - `@emotion`: CSS-in-JS styling
- **Axios**: HTTP client

### Backend Stack
- **Flask 3.0**: Lightweight web framework
- **LangChain 0.1**: LLM orchestration
  - Document loaders
  - Text splitters
  - Embeddings
  - Vector stores
  - Chains
- **ChromaDB 0.4**: Vector database
- **Google Generative AI**: LLM provider
- **OCR Libraries**:
  - pytesseract: Tesseract OCR wrapper
  - Pillow: Image processing
  - PyPDF2: PDF text extraction
  - pdf2image: PDF to image conversion

## Security Considerations

### Current Implementation
- CORS enabled for local development
- File type validation
- File size limits (10MB)
- API key in environment variables

### Production Recommendations
1. **Authentication**: Add user authentication
2. **Authorization**: Role-based access control
3. **Rate Limiting**: Prevent abuse
4. **Input Validation**: Sanitize all inputs
5. **HTTPS**: SSL/TLS encryption
6. **API Key Management**: Use secret management service
7. **File Scanning**: Antivirus scanning
8. **Content Security Policy**: XSS protection

## Scalability Considerations

### Current Limitations
- Single-threaded Flask server
- Local ChromaDB storage
- In-memory file metadata
- No caching

### Scaling Recommendations
1. **Application Server**: Use Gunicorn/uWSGI
2. **Load Balancer**: Nginx or cloud load balancer
3. **Vector DB**: Migrate to hosted ChromaDB or Pinecone
4. **Caching**: Redis for session/response caching
5. **Queue System**: Celery for async processing
6. **File Storage**: S3 or cloud storage
7. **Database**: PostgreSQL for metadata
8. **Monitoring**: Add logging and metrics

## Configuration

### Environment Variables

**Backend (.env)**
```
GEMINI_API_KEY=your_api_key
```

**Frontend (.env)**
```
VITE_API_BASE_URL=http://localhost:5000
```

### RAG Configuration (rag_pipeline.py)
```python
CHUNK_SIZE = 1000        # Characters per chunk
CHUNK_OVERLAP = 200      # Character overlap between chunks
CHROMA_PERSIST_DIR = "./chroma_store"
```

### LLM Configuration
```python
# Embeddings Model
model="models/embedding-001"

# Generation Model
model="gemini-pro"
temperature=0.3
```

## Performance Optimization

### Current Optimizations
1. Text chunking with overlap for context preservation
2. Semantic search with top-K retrieval
3. Persistent vector store (no re-indexing)

### Future Optimizations
1. **Streaming Responses**: Stream LLM output
2. **Batch Processing**: Batch embed multiple documents
3. **Caching**: Cache frequent queries
4. **Compression**: Compress stored embeddings
5. **Index Optimization**: Tune ChromaDB settings
6. **Lazy Loading**: Load components on demand

## Error Handling

### Frontend
- Network errors caught and displayed
- Loading states for async operations
- Snackbar notifications for user feedback
- Error boundaries (can be added)

### Backend
- Try-catch blocks around operations
- Detailed error messages
- HTTP status codes
- Logging to console

## Testing Strategy

### Recommended Tests

**Frontend**
- Component unit tests (Jest + React Testing Library)
- Integration tests for API calls
- E2E tests (Cypress/Playwright)

**Backend**
- Unit tests for utilities (pytest)
- Integration tests for endpoints
- OCR accuracy tests
- RAG quality tests

## Monitoring and Observability

### Recommended Tools
1. **Logging**: Python logging, Winston (Node)
2. **Metrics**: Prometheus
3. **Tracing**: OpenTelemetry
4. **Error Tracking**: Sentry
5. **Analytics**: Google Analytics, Mixpanel

---

This architecture provides a solid foundation for an AI-powered customer support system with RAG capabilities. It can be extended and scaled based on specific requirements and use cases.

