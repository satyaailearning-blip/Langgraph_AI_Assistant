import os
import sys
import asyncio
import shutil

from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse

# Ensure Agents directory is in sys.path for imports to work
sys.path.insert(0, os.path.dirname(__file__))

from graph_builder import build_graph
from rag.vector_store import load_vector_db, create_vector_db

app = FastAPI()
graph = build_graph()

# Initialize vector DB at startup
@app.on_event("startup")
async def startup_event():
    """Initialize vector database on app startup."""
    print("=" * 50)
    print("Initializing Vector Database...")
    print("=" * 50)
    
    try:
        # Try to load existing vector DB
        db = load_vector_db()
        print("✓ Vector DB loaded successfully!")
    except Exception as load_error:
        # Any error loading (FileNotFoundError, FAISS error, etc.) means we need to create
        print(f"Vector DB not found or corrupted. Creating from documents...")
        print(f"(Load error: {type(load_error).__name__})")
        try:
            db = create_vector_db()
            print("✓ Vector DB created successfully!")
        except Exception as create_error:
            print(f"✗ Error creating vector DB: {create_error}")
            print("RAG functionality may not be available")
            import traceback
            traceback.print_exc()


@app.get("/")
def home():
    return {"status": "WhatsApp AI Assistant is running"}


@app.get("/health")
def health_check():
    """Health check endpoint to verify vector DB status."""
    try:
        from rag.vector_store import load_vector_db
        db = load_vector_db()
        return {
            "status": "healthy",
            "vector_db": "ready",
            "message": "WhatsApp AI Assistant is fully operational with RAG capability"
        }
    except FileNotFoundError:
        return {
            "status": "initializing",
            "vector_db": "not_ready",
            "message": "Vector DB still being created. Please wait..."
        }
    except Exception as e:
        return {
            "status": "error",
            "vector_db": "failed",
            "message": f"Error: {str(e)}"
        }


@app.post("/rebuild-vector-db")
async def rebuild_vector_db():
    """
    Manually rebuild vector database from documents.
    Useful when documents are added/removed/updated.
    """
    print("=" * 60)
    print("MANUAL VECTOR DB REBUILD INITIATED")
    print("=" * 60)
    
    try:
        # Step 1: Delete existing vector DB
        vector_db_path = os.path.join(os.path.dirname(__file__), "data", "vector_db")
        
        if os.path.exists(vector_db_path):
            print(f"🗑️  Deleting existing vector DB at: {vector_db_path}")
            shutil.rmtree(vector_db_path)
            print("✓ Existing vector DB deleted")
        else:
            print(f"ℹ️  Vector DB path does not exist: {vector_db_path}")
        
        # Step 2: Create fresh vector DB from documents
        print("🔄 Creating fresh vector DB from documents...")
        db = create_vector_db()
        
        print("=" * 60)
        print("✓✓✓ VECTOR DB REBUILD SUCCESSFUL ✓✓✓")
        print("=" * 60)
        
        return {
            "status": "success",
            "message": "Vector database rebuilt successfully",
            "vector_db_path": vector_db_path,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
    except Exception as e:
        print("=" * 60)
        print(f"✗✗✗ VECTOR DB REBUILD FAILED ✗✗✗")
        print(f"Error: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        
        return {
            "status": "failed",
            "error": str(e),
            "message": "Failed to rebuild vector database"
        }


@app.get("/whatsapp")
def whatsapp_get():
    return {"message": "This endpoint only accepts POST requests from Twilio."}


@app.post("/whatsapp")
async def whatsapp_reply(request: Request, Body: str = Form(...)):
    client = request.client
    if client:
        print(f"Incoming WhatsApp request from {client.host}:{client.port}")

    print("Incoming message:", Body)

    user_question = Body.strip()

    try:
        result = graph.invoke({
            "question": user_question
        })

        answer = result.get("answer", "")
        if not answer:
            answer = "Sorry, I couldn't generate an answer right now."

    except Exception as e:
        print("Error while generating answer:", e)
        answer = "Sorry, something went wrong while processing your message."

    if len(answer) > 1500:
        answer = answer[:1500] + "..."

    print("Generated answer:", answer)

    response = MessagingResponse()
    response.message(answer)

    return PlainTextResponse(str(response), media_type="application/xml")


