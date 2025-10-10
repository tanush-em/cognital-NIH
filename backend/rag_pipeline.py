"""
RAG Pipeline using LangChain, ChromaDB, and Google Gemini
"""
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CHROMA_PERSIST_DIR = "./chroma_store"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Initialize vector store
vectorstore = None


def get_vectorstore():
    """Get or create the ChromaDB vectorstore"""
    global vectorstore
    if vectorstore is None:
        vectorstore = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=embeddings
        )
    return vectorstore


def add_document_to_store(text, metadata=None):
    """
    Add a document to the vector store
    
    Args:
        text: The text content to add
        metadata: Optional metadata dictionary
        
    Returns:
        Number of chunks added
    """
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    
    chunks = text_splitter.split_text(text)
    
    # Create documents with metadata
    documents = [
        Document(page_content=chunk, metadata=metadata or {})
        for chunk in chunks
    ]
    
    # Add to vector store
    store = get_vectorstore()
    store.add_documents(documents)
    store.persist()
    
    return len(chunks)


def query_documents(query, k=4):
    """
    Query the vector store and get AI response
    
    Args:
        query: User's question
        k: Number of relevant chunks to retrieve
        
    Returns:
        AI generated answer
    """
    store = get_vectorstore()
    
    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
        convert_system_message_to_human=True
    )
    
    # Create retrieval QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=store.as_retriever(search_kwargs={"k": k}),
        return_source_documents=True
    )
    
    # Get response
    result = qa_chain({"query": query})
    
    return {
        "answer": result["result"],
        "source_documents": [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in result.get("source_documents", [])
        ]
    }


def get_document_count():
    """Get the number of documents in the vector store"""
    try:
        store = get_vectorstore()
        collection = store._collection
        return collection.count()
    except:
        return 0

