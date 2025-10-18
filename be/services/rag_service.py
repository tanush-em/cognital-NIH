"""
RAG (Retrieval-Augmented Generation) service using ChromaDB
"""
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging
from .pdf_processor import pdf_processor

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        """Initialize RAG service with ChromaDB"""
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection("telecom_knowledge")
        except:
            self.collection = self.client.create_collection(
                name="telecom_knowledge",
                metadata={"description": "Telecom support knowledge base"}
            )
        
        # Auto-load PDFs from resources folder
        self._auto_load_pdfs()
    
    def _auto_load_pdfs(self):
        """Automatically load PDFs from resources folder on startup"""
        try:
            # Get documents from PDF processor
            pdf_documents = pdf_processor.get_documents_for_rag()
            
            if pdf_documents:
                logger.info(f"Auto-loading {len(pdf_documents)} PDF documents from resources folder")
                success = self.add_documents(pdf_documents)
                if success:
                    logger.info("Successfully auto-loaded PDF documents")
                else:
                    logger.warning("Failed to auto-load some PDF documents")
            else:
                logger.info("No PDF documents found in resources folder")
                
        except Exception as e:
            logger.error(f"Error auto-loading PDFs: {str(e)}")
    
    def reload_pdfs(self) -> bool:
        """Reload all PDFs from resources folder"""
        try:
            # Clear existing collection
            self.collection.delete(where={})
            
            # Reload PDFs
            self._auto_load_pdfs()
            return True
            
        except Exception as e:
            logger.error(f"Error reloading PDFs: {str(e)}")
            return False
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the knowledge base"""
        try:
            texts = []
            metadatas = []
            ids = []
            
            for i, doc in enumerate(documents):
                texts.append(doc['content'])
                metadatas.append({
                    'title': doc.get('title', ''),
                    'category': doc.get('category', ''),
                    'source': doc.get('source', '')
                })
                ids.append(f"doc_{i}")
            
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to knowledge base")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return False
    
    def search_relevant_docs(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents using semantic similarity"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            relevant_docs = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    relevant_docs.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def get_context_for_query(self, query: str, max_context_length: int = 2000) -> str:
        """Get relevant context for a query"""
        relevant_docs = self.search_relevant_docs(query)
        
        context_parts = []
        current_length = 0
        
        for doc in relevant_docs:
            content = doc['content']
            if current_length + len(content) <= max_context_length:
                context_parts.append(content)
                current_length += len(content)
            else:
                break
        
        return "\n\n".join(context_parts)
    
    def calculate_confidence(self, query: str, response: str) -> float:
        """Calculate confidence score for a response based on relevant documents"""
        relevant_docs = self.search_relevant_docs(query, n_results=3)
        
        if not relevant_docs:
            return 0.3  # Low confidence if no relevant docs found
        
        # Calculate average similarity
        avg_distance = sum(doc['distance'] for doc in relevant_docs) / len(relevant_docs)
        
        # Convert distance to confidence (lower distance = higher confidence)
        confidence = max(0.1, 1.0 - avg_distance)
        
        return min(1.0, confidence)

# Global RAG service instance
rag_service = RAGService()
