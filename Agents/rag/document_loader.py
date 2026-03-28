import os
import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


def _get_data_folder():
    # robust path for local and Docker: locate from this file's directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_path = os.path.join(base_dir, "data", "documents")
    logger.info(f"📂 Resolved documents folder path: {data_path}")
    logger.info(f"📂 Path exists: {os.path.isdir(data_path)}")
    if os.path.isdir(data_path):
        files = os.listdir(data_path)
        logger.info(f"📂 Files found: {files}")
    return data_path


def load_documents():
    docs = []
    folder_path = _get_data_folder()

    if not os.path.isdir(folder_path):
        logger.error(f"❌ Document folder path does not exist: {folder_path}")
        logger.error(f"❌ Current working directory: {os.getcwd()}")
        logger.error(f"❌ Contents of parent: {os.listdir(os.path.dirname(folder_path)) if os.path.isdir(os.path.dirname(folder_path)) else 'Parent does not exist'}")
        raise FileNotFoundError(f"Document folder not found: {folder_path}")

    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    logger.info(f"📄 Found {len(pdf_files)} PDF files: {pdf_files}")
    
    for file in pdf_files:
        file_path = os.path.join(folder_path, file)
        logger.info(f"📄 Loading PDF: {file_path}")
        loader = PyPDFLoader(file_path)
        docs.extend(loader.load())

    logger.info(f"✓ Loaded {len(docs)} total document pages")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    split_docs = splitter.split_documents(docs)
    logger.info(f"✓ Split into {len(split_docs)} chunks")
    return split_docs