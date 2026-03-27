"""
Initialization script to create vector DB from documents on startup.
Runs once, checks if vector DB exists, creates if missing.
"""

import os
import sys
from pathlib import Path

# Add Agents to path
agents_dir = os.path.join(os.path.dirname(__file__), "Agents")
sys.path.insert(0, agents_dir)

from rag.vector_store import create_vector_db, load_vector_db


def init_vector_db():
    """Initialize vector database if it doesn't exist."""
    
    base_dir = os.path.join(os.path.dirname(__file__), "Agents")
    vector_db_path = os.path.join(base_dir, "data", "vector_db")
    
    # Check if vector DB already exists
    if os.path.exists(vector_db_path):
        print(f"✓ Vector DB already exists at {vector_db_path}")
        try:
            db = load_vector_db()
            print("✓ Vector DB loaded successfully!")
            return True
        except Exception as e:
            print(f"✗ Error loading vector DB: {e}")
            print("Will recreate vector DB...")
    
    # Create vector DB from documents
    print("Creating vector DB from documents...")
    try:
        db = create_vector_db()
        print("✓ Vector DB created successfully!")
        return True
    except Exception as e:
        print(f"✗ Error creating vector DB: {e}")
        print("RAG functionality will not be available")
        return False


if __name__ == "__main__":
    init_vector_db()
