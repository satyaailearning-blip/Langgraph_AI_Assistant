from dotenv import load_dotenv
import os
import logging

load_dotenv()

from rag.document_loader import load_documents
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_vector_db_path():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, "data", "vector_db")


def create_vector_db():
    """Create vector database from documents with detailed logging."""
    vector_db_path = _get_vector_db_path()
    
    logger.info("=" * 60)
    logger.info("VECTOR DB CREATION STARTED")
    logger.info("=" * 60)
    
    try:
        logger.info(f"📁 Vector DB Path: {vector_db_path}")
        logger.info(f"📁 Ensuring directory exists...")
        os.makedirs(vector_db_path, exist_ok=True)
        logger.info(f"✓ Directory ready: {vector_db_path}")
        
        logger.info("📄 Loading documents...")
        docs = load_documents()
        
        if not docs:
            logger.error("❌ No documents were loaded!")
            raise ValueError("No documents found to create vector DB")
            
        logger.info(f"✓ Loaded {len(docs)} document chunks")
        
        logger.info("🔑 Creating embeddings...")
        embeddings = OpenAIEmbeddings()
        logger.info("✓ OpenAI embeddings initialized")
        
        logger.info("🏢 Building FAISS index...")
        db = FAISS.from_documents(docs, embeddings)
        logger.info("✓ FAISS index built successfully")
        
        logger.info("💾 Saving vector database...")
        db.save_local(vector_db_path)
        logger.info(f"✓ Vector database saved at: {vector_db_path}")
        
        # Verify files were created
        saved_files = os.listdir(vector_db_path)
        logger.info(f"✓ Created files: {saved_files}")
        
        logger.info("=" * 60)
        logger.info("✓✓✓ VECTOR DB CREATION SUCCESSFUL ✓✓✓")
        logger.info("=" * 60)
        
        return db
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"✗✗✗ VECTOR DB CREATION FAILED ✗✗✗")
        logger.error(f"Error Type: {type(e).__name__}")
        logger.error(f"Error Message: {str(e)}")
        logger.error("=" * 60)
        raise


def load_vector_db():
    """Load existing vector database with detailed logging."""
    embeddings = OpenAIEmbeddings()
    vector_db_path = _get_vector_db_path()
    
    logger.info("=" * 60)
    logger.info("VECTOR DB LOADING STARTED")
    logger.info("=" * 60)
    logger.info(f"📁 Looking for Vector DB at: {vector_db_path}")

    # Check if path exists AND contains FAISS index files
    if not os.path.exists(vector_db_path):
        logger.warning(f"✗ Vector DB path does not exist: {vector_db_path}")
        raise FileNotFoundError(f"Vector DB not found at: {vector_db_path}")
    
    # Check if FAISS index file exists
    index_file = os.path.join(vector_db_path, "index.faiss")
    if not os.path.exists(index_file):
        logger.warning(f"✗ FAISS index file not found: {index_file}")
        raise FileNotFoundError(f"FAISS index file not found at: {index_file}")

    try:
        logger.info("🔄 Loading FAISS index...")
        db = FAISS.load_local(
            vector_db_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info("✓ FAISS index loaded successfully")
        logger.info("=" * 60)
        logger.info("✓✓✓ VECTOR DB LOADED SUCCESSFULLY ✓✓✓")
        logger.info("=" * 60)
        return db
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"✗✗✗ VECTOR DB LOADING FAILED ✗✗✗")
        logger.error(f"Error: {str(e)}")
        logger.error("=" * 60)
        raise


def retrieve_docs(query):
    db = load_vector_db()

    docs = db.similarity_search(query, k=3)

    context = "\n\n".join([doc.page_content for doc in docs])

    return context