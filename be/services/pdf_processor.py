"""
PDF Processing Service with OCR capabilities
Handles PDF text extraction and OCR for scanned documents
"""
import os
import logging
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdfplumber import PDF
import io

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, resources_folder: str = "resources"):
        """Initialize PDF processor with resources folder path"""
        self.resources_folder = resources_folder
        self.supported_formats = ['.pdf']
        
        # Ensure resources folder exists
        if not os.path.exists(self.resources_folder):
            os.makedirs(self.resources_folder)
            logger.info(f"Created resources folder: {self.resources_folder}")
    
    def get_pdf_files(self) -> List[str]:
        """Get all PDF files from the resources folder"""
        pdf_files = []
        if not os.path.exists(self.resources_folder):
            return pdf_files
            
        for filename in os.listdir(self.resources_folder):
            if filename.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(self.resources_folder, filename))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {self.resources_folder}")
        return pdf_files
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from PDF using multiple methods"""
        try:
            # Method 1: Try PyMuPDF first (fastest for text-based PDFs)
            text_content = self._extract_with_pymupdf(pdf_path)
            
            # Method 2: If no text found, try pdfplumber
            if not text_content.strip():
                text_content = self._extract_with_pdfplumber(pdf_path)
            
            # Method 3: If still no text, use OCR
            if not text_content.strip():
                text_content = self._extract_with_ocr(pdf_path)
            
            return {
                'file_path': pdf_path,
                'filename': os.path.basename(pdf_path),
                'content': text_content,
                'extraction_method': 'pymupdf' if text_content else 'ocr',
                'success': bool(text_content.strip())
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return {
                'file_path': pdf_path,
                'filename': os.path.basename(pdf_path),
                'content': '',
                'extraction_method': 'failed',
                'success': False,
                'error': str(e)
            }
    
    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (fastest for text-based PDFs)"""
        try:
            doc = fitz.open(pdf_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_content.append(f"--- Page {page_num + 1} ---\n{text}")
            
            doc.close()
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed for {pdf_path}: {str(e)}")
            return ""
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber (good for complex layouts)"""
        try:
            text_content = []
            with PDF(open(pdf_path, 'rb')) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        text_content.append(f"--- Page {page_num + 1} ---\n{text}")
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed for {pdf_path}: {str(e)}")
            return ""
    
    def _extract_with_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR (for scanned PDFs)"""
        try:
            doc = fitz.open(pdf_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # Increase resolution for better OCR
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Convert to PIL Image
                image = Image.open(io.BytesIO(img_data))
                
                # Preprocess image for better OCR
                processed_image = self._preprocess_image_for_ocr(image)
                
                # Extract text using OCR
                text = pytesseract.image_to_string(processed_image, lang='eng')
                
                if text.strip():
                    text_content.append(f"--- Page {page_num + 1} (OCR) ---\n{text}")
            
            doc.close()
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.warning(f"OCR extraction failed for {pdf_path}: {str(e)}")
            return ""
    
    def _preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Preprocess image to improve OCR accuracy"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply image preprocessing
            # 1. Denoise
            img_array = cv2.medianBlur(img_array, 3)
            
            # 2. Increase contrast
            img_array = cv2.convertScaleAbs(img_array, alpha=1.2, beta=10)
            
            # 3. Apply threshold to get binary image
            _, img_array = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Convert back to PIL Image
            return Image.fromarray(img_array)
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {str(e)}")
            return image
    
    def process_all_pdfs(self) -> List[Dict[str, Any]]:
        """Process all PDF files in the resources folder"""
        pdf_files = self.get_pdf_files()
        processed_documents = []
        
        for pdf_path in pdf_files:
            logger.info(f"Processing PDF: {pdf_path}")
            result = self.extract_text_from_pdf(pdf_path)
            processed_documents.append(result)
        
        successful_extractions = [doc for doc in processed_documents if doc['success']]
        logger.info(f"Successfully processed {len(successful_extractions)} out of {len(pdf_files)} PDF files")
        
        return processed_documents
    
    def get_documents_for_rag(self) -> List[Dict[str, Any]]:
        """Get processed documents formatted for RAG ingestion"""
        processed_docs = self.process_all_pdfs()
        rag_documents = []
        
        for doc in processed_docs:
            if doc['success'] and doc['content'].strip():
                rag_documents.append({
                    'content': doc['content'],
                    'title': doc['filename'],
                    'source': 'pdf_file',
                    'file_path': doc['file_path'],
                    'extraction_method': doc['extraction_method']
                })
        
        return rag_documents
    
    def add_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single PDF file and return the result"""
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f"File not found: {file_path}"
            }
        
        if not file_path.lower().endswith('.pdf'):
            return {
                'success': False,
                'error': f"File is not a PDF: {file_path}"
            }
        
        return self.extract_text_from_pdf(file_path)

# Global PDF processor instance
pdf_processor = PDFProcessor()
