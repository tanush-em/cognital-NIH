# System Dependencies - Installation Status

## ✅ Installed Dependencies

### 1. Tesseract OCR (v5.5.1)
- **Purpose**: Text extraction from images
- **Location**: `/opt/homebrew/bin/tesseract`
- **Status**: ✅ Installed and working

### 2. Poppler (v25.10.0)
- **Purpose**: PDF to image conversion (for pdf2image Python package)
- **Location**: `/opt/homebrew/bin/pdftoppm`
- **Status**: ✅ Installed and working

## How These Are Used

### PDF Processing Flow:
1. User uploads PDF → Backend receives file
2. PyPDF2 tries to extract text directly
3. If no text found (scanned PDF):
   - pdf2image converts PDF pages to images using **poppler**
   - Images are processed by **tesseract** OCR
4. Extracted text is chunked and stored in ChromaDB

### Image Processing Flow:
1. User uploads image (JPG/PNG/etc)
2. pytesseract processes it using **tesseract**
3. Extracted text is chunked and stored

## Verification Commands

```bash
# Check if installed
which tesseract    # Should show: /opt/homebrew/bin/tesseract
which pdftoppm     # Should show: /opt/homebrew/bin/pdftoppm

# Check versions
tesseract --version
pdftoppm -v

# Test OCR (optional)
tesseract --list-langs  # Shows available languages
```

## If You Need to Reinstall

```bash
# macOS
brew install tesseract poppler

# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# Windows
# Download and install manually:
# - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
# - Poppler: http://blog.alivate.com.au/poppler-windows/
```

## Troubleshooting

### "Unable to get page count. Is poppler installed?"
- **Solution**: Run `brew install poppler` (macOS)
- **Verify**: Run `which pdftoppm` - should show path

### "tesseract is not installed or it's not in your PATH"
- **Solution**: Run `brew install tesseract` (macOS)
- **Verify**: Run `which tesseract` - should show path

### On Windows: "tesseract not found"
Add to your `backend/ocr_utils.py`:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Current Status

✅ **macOS System (Your Setup)**
- Tesseract: Installed ✓
- Poppler: Installed ✓
- Python venv: Configured ✓
- Backend: Ready to process PDFs and images ✓

## Next Steps

Your backend can now process:
- ✅ PDF files (with text)
- ✅ Scanned PDFs (will use OCR)
- ✅ Image files (JPG, PNG, BMP, TIFF)

Just restart your backend server:
```bash
./start-backend.sh
```

Then try uploading a PDF - it should work now!

