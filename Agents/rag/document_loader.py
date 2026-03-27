import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def _get_data_folder():
    # robust path for local and Docker: locate from this file's directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, "data", "documents")


def load_documents():
    docs = []
    folder_path = _get_data_folder()

    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"Document folder not found: {folder_path}")

    for file in os.listdir(folder_path):
        if file.lower().endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(folder_path, file))
            docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    split_docs = splitter.split_documents(docs)
    return split_docs