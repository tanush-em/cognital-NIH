# Resources Folder

This folder contains PDF files that serve as the knowledge base for the RAG (Retrieval-Augmented Generation) system.

## How it works

1. **Automatic Loading**: When the application starts, it automatically scans this folder for PDF files
2. **Text Extraction**: Each PDF is processed using multiple methods:
   - PyMuPDF for text-based PDFs (fastest)
   - pdfplumber for complex layouts
   - OCR (Tesseract) for scanned documents
3. **RAG Integration**: Extracted text is automatically added to the ChromaDB knowledge base
4. **Real-time Updates**: New PDFs added to this folder can be processed via API endpoints

## Supported File Types

- **PDF files only** (.pdf extension)
- Both text-based and scanned PDFs are supported
- OCR is automatically applied for scanned documents

## File Management

### Adding PDFs
- Simply copy PDF files to this folder
- Use the `/api/upload-pdf` endpoint for programmatic uploads
- Use the `/api/reload-pdfs` endpoint to reprocess all files

### File Organization
- Keep PDFs organized by topic or category
- Use descriptive filenames for better identification
- Large files may take longer to process

## API Endpoints

- `GET /api/pdfs` - List all PDF files in the folder
- `POST /api/upload-pdf` - Upload a new PDF file
- `POST /api/reload-pdfs` - Reload all PDFs from the folder

## Processing Methods

1. **Text-based PDFs**: Direct text extraction (fastest)
2. **Scanned PDFs**: OCR processing with image preprocessing
3. **Mixed content**: Combination of text extraction and OCR

## Performance Notes

- Processing time depends on PDF size and complexity
- OCR processing is slower but handles scanned documents
- Large files are automatically chunked for better performance
- Processing happens in the background to avoid blocking the API

## Troubleshooting

- Check file permissions for the resources folder
- Ensure PDF files are not corrupted
- Monitor application logs for processing errors
- Use the test script to verify PDF processing: `python test_pdf_integration.py`
