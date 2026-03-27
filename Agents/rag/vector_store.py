from dotenv import load_dotenv
import os

load_dotenv()

from rag.document_loader import load_documents
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


def _get_vector_db_path():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, "data", "vector_db")


def create_vector_db():
    print("Loading documents...")
    docs = load_documents()

    print("Creating embeddings...")
    embeddings = OpenAIEmbeddings()

    db = FAISS.from_documents(docs, embeddings)
    vector_db_path = _get_vector_db_path()
    os.makedirs(vector_db_path, exist_ok=True)
    db.save_local(vector_db_path)

    print("Vector database created successfully!", vector_db_path)
    return db


def load_vector_db():
    embeddings = OpenAIEmbeddings()
    vector_db_path = _get_vector_db_path()

    if not os.path.exists(vector_db_path):
        raise FileNotFoundError(f"Vector DB not found at: {vector_db_path}. Run create_vector_db() first.")

    db = FAISS.load_local(
        vector_db_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return db


def retrieve_docs(query):
    db = load_vector_db()

    docs = db.similarity_search(query, k=3)

    context = "\n\n".join([doc.page_content for doc in docs])

    return context