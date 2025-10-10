"""
OCR Utilities for extracting text from images and PDFs
"""
import pytesseract
from PIL import Image
import io
import PyPDF2
from pdf2image import convert_from_bytes


def extract_text_from_image(image_bytes):
    """
    Extract text from an image using Tesseract OCR
    
    Args:
        image_bytes: Binary image data
        
    Returns:
        Extracted text as string
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from image: {str(e)}")


def extract_text_from_pdf(pdf_bytes):
    """
    Extract text from PDF, using OCR if necessary
    
    Args:
        pdf_bytes: Binary PDF data
        
    Returns:
        Extracted text as string
    """
    try:
        # First try to extract text directly
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        # If no text extracted, use OCR
        if not text.strip():
            print("No text found in PDF, using OCR...")
            images = convert_from_bytes(pdf_bytes)
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
        
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def extract_text(file_bytes, filename):
    """
    Extract text from a file based on its extension
    
    Args:
        file_bytes: Binary file data
        filename: Name of the file with extension
        
    Returns:
        Extracted text as string
    """
    file_ext = filename.lower().split('.')[-1]
    
    if file_ext == 'pdf':
        return extract_text_from_pdf(file_bytes)
    elif file_ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
        return extract_text_from_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

