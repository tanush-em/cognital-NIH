"""
Flask backend for AI-First Customer Support chatbot
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

from ocr_utils import extract_text
from rag_pipeline import add_document_to_store, query_documents, get_document_count

app = Flask(__name__)
CORS(app)

# Store uploaded file metadata
uploaded_files = []


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "documents_count": get_document_count()
    })


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload and process document endpoint
    
    Accepts PDF or image files, extracts text using OCR,
    and stores embeddings in ChromaDB
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read file bytes
        file_bytes = file.read()
        filename = file.filename
        
        print(f"Processing file: {filename}")
        
        # Extract text using OCR
        try:
            text = extract_text(file_bytes, filename)
            
            if not text.strip():
                return jsonify({"error": "No text could be extracted from the file"}), 400
            
            print(f"Extracted {len(text)} characters")
            
        except Exception as e:
            return jsonify({"error": f"Text extraction failed: {str(e)}"}), 500
        
        # Add to vector store
        try:
            metadata = {
                "filename": filename,
                "upload_date": datetime.now().isoformat()
            }
            
            chunks_count = add_document_to_store(text, metadata)
            
            # Store file metadata
            uploaded_files.append({
                "filename": filename,
                "upload_date": metadata["upload_date"],
                "chunks": chunks_count,
                "text_length": len(text)
            })
            
            print(f"Added {chunks_count} chunks to vector store")
            
            return jsonify({
                "message": "File uploaded and processed successfully",
                "filename": filename,
                "chunks_added": chunks_count,
                "text_length": len(text)
            }), 200
            
        except Exception as e:
            return jsonify({"error": f"Failed to add to vector store: {str(e)}"}), 500
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@app.route('/query', methods=['POST'])
def query():
    """
    Query endpoint for RAG-based question answering
    
    Takes user query, retrieves relevant chunks from ChromaDB,
    and generates answer using Gemini
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400
        
        user_query = data['query']
        
        if not user_query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400
        
        print(f"Received query: {user_query}")
        
        # Check if there are any documents
        if get_document_count() == 0:
            return jsonify({
                "answer": "I don't have any documents to reference yet. Please upload some documents first.",
                "source_documents": []
            }), 200
        
        # Query the RAG pipeline
        try:
            result = query_documents(user_query)
            
            return jsonify({
                "answer": result["answer"],
                "source_documents": result["source_documents"]
            }), 200
            
        except Exception as e:
            return jsonify({"error": f"Query processing failed: {str(e)}"}), 500
        
    except Exception as e:
        print(f"Query error: {str(e)}")
        return jsonify({"error": f"Query failed: {str(e)}"}), 500


@app.route('/documents', methods=['GET'])
def list_documents():
    """List all uploaded documents"""
    return jsonify({
        "documents": uploaded_files,
        "total_count": len(uploaded_files),
        "total_chunks": get_document_count()
    }), 200


@app.route('/clear', methods=['POST'])
def clear_documents():
    """Clear all documents from the vector store"""
    try:
        # This would require additional implementation in rag_pipeline.py
        # For now, just clear the uploaded files list
        uploaded_files.clear()
        return jsonify({"message": "Documents list cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Ensure chroma_store directory exists
    os.makedirs('./chroma_store', exist_ok=True)
    
    print("Starting AI-First Customer Support Backend...")
    print(f"Documents in store: {get_document_count()}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

