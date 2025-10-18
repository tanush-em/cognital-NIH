#!/usr/bin/env python3
"""
Test script for PDF OCR and RAG integration
"""
import os
import sys
import logging
from services.pdf_processor import pdf_processor
from services.rag_service import rag_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pdf_processor():
    """Test PDF processor functionality"""
    print("🔍 Testing PDF Processor...")
    
    # Test getting PDF files
    pdf_files = pdf_processor.get_pdf_files()
    print(f"📁 Found {len(pdf_files)} PDF files in resources folder")
    
    if pdf_files:
        for pdf_path in pdf_files:
            print(f"  - {os.path.basename(pdf_path)}")
    
    # Test processing all PDFs
    print("\n📄 Processing PDFs...")
    processed_docs = pdf_processor.process_all_pdfs()
    
    successful = [doc for doc in processed_docs if doc['success']]
    failed = [doc for doc in processed_docs if not doc['success']]
    
    print(f"✅ Successfully processed: {len(successful)}")
    print(f"❌ Failed to process: {len(failed)}")
    
    for doc in successful:
        print(f"  📄 {doc['filename']} - Method: {doc['extraction_method']} - Content length: {len(doc['content'])}")
    
    for doc in failed:
        print(f"  ❌ {doc['filename']} - Error: {doc.get('error', 'Unknown error')}")
    
    return successful

def test_rag_integration():
    """Test RAG service integration"""
    print("\n🧠 Testing RAG Integration...")
    
    # Test getting documents for RAG
    rag_documents = pdf_processor.get_documents_for_rag()
    print(f"📚 Found {len(rag_documents)} documents ready for RAG")
    
    for doc in rag_documents:
        print(f"  📄 {doc['title']} - Source: {doc['source']} - Method: {doc['extraction_method']}")
    
    # Test RAG service
    if rag_documents:
        print("\n🔍 Testing RAG search...")
        
        # Test queries
        test_queries = [
            "What is this document about?",
            "Key information",
            "Important details"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            context = rag_service.get_context_for_query(query, max_context_length=500)
            if context:
                print(f"📝 Context found: {len(context)} characters")
                print(f"Preview: {context[:200]}...")
            else:
                print("❌ No context found")

def test_health_check():
    """Test system health"""
    print("\n🏥 Health Check...")
    
    try:
        # Test PDF processor
        pdf_files = pdf_processor.get_pdf_files()
        print(f"✅ PDF Processor: {len(pdf_files)} files found")
        
        # Test RAG service
        collection_count = rag_service.collection.count()
        print(f"✅ RAG Service: {collection_count} documents in knowledge base")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 PDF OCR and RAG Integration Test")
    print("=" * 50)
    
    # Check if resources folder exists
    if not os.path.exists('resources'):
        print("📁 Creating resources folder...")
        os.makedirs('resources')
        print("✅ Resources folder created")
        print("💡 Add PDF files to the 'resources' folder to test the system")
        return
    
    # Run tests
    try:
        # Health check
        if not test_health_check():
            print("❌ System health check failed")
            return
        
        # Test PDF processor
        successful_docs = test_pdf_processor()
        
        # Test RAG integration
        test_rag_integration()
        
        print("\n🎉 Test completed successfully!")
        
        if successful_docs:
            print(f"✅ {len(successful_docs)} PDF documents are ready for use in the RAG system")
        else:
            print("💡 No PDF documents were processed. Add PDF files to the 'resources' folder and run the test again.")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        logger.exception("Test failed")

if __name__ == "__main__":
    main()
