# LangGraph AI Assistant - Complete Project Documentation

**Date:** March 28, 2026  
**Project:** WhatsApp AI Assistant with RAG (Retrieval-Augmented Generation)

---

## Table of Contents
1. Project Goal
2. Complete Workflow Sequence
3. Application Architecture
4. RAG System Overview
5. Deployment Pipeline
6. Key Components
7. Current Issue & Solution
8. Success Indicators

---

## 1. Project Goal

Build an **AI-powered WhatsApp Assistant** that answers questions using:

- **General AI Knowledge** - for general/common questions using OpenAI GPT
- **Your Documents** - for specific business/technical questions via RAG (Vector Database)

The assistant intelligently routes incoming messages to the appropriate agent based on content.

---

## 2. Complete Workflow Sequence

### Message Flow

```
Incoming WhatsApp Message
         ↓
FastAPI Server receives request
         ↓
Router Agent analyzes message
         ↓
    ┌────────────┴────────────┐
    ↓                         ↓
General Agent          RAG Agent
(OpenAI GPT)          (Vector DB + GPT)
    ↓                         ↓
    └────────────┬────────────┘
                 ↓
          Generate Answer
                 ↓
      Send Response to WhatsApp
```

### Data Flow (RAG Initialization)

```
Application Startup
         ↓
Vector Store Module Initializes
         ↓
Check if vector DB exists?
    ╱───────────┴───────────╲
   YES                       NO
    ↓                        ↓
Load existing DB      Create from scratch
    ↓                        ↓
                    Load PDFs from documents/
                             ↓
                    Split into chunks
                    (1000 chars, 200 overlap)
                             ↓
                    Create embeddings
                    (OpenAI API)
                             ↓
                    Store in FAISS index
                             ↓
                    Save to disk
                             ↓
          Vector DB Ready ✓
```

---

## 3. Application Architecture

### Directory Structure

```
Langgraph_AI_Assistant/
├── Agents/
│   ├── app.py                 # Main agent/graph setup
│   ├── main.py                # Entry point
│   ├── whatsapp_app.py        # FastAPI server (port 8000)
│   ├── router_agent.py        # Message router (general vs RAG)
│   ├── test_agent.py          # Testing utilities
│   ├── graph_builder.py       # LangGraph workflow builder
│   ├── requirements.txt       # Python dependencies
│   ├── data/
│   │   ├── documents/         # Source PDFs (input)
│   │   │   ├── FEED_SOW_IA1234.pdf
│   │   │   ├── uad_LTDP_adequacy_report.pdf
│   │   │   └── uad_ltdp2_sow.pdf
│   │   └── vector_db/         # Generated FAISS index (output)
│   │       ├── index.faiss
│   │       └── [index files]
│   └── rag/
│       ├── vector_store.py    # Vector DB creation/loading
│       └── document_loader.py # PDF loading & chunking
├── Dockerfile                 # Container configuration
├── .dockerignore              # Docker build exclusions
├── init_db.py                 # Vector DB initialization script
├── .env                       # Environment variables
└── render.yaml                # Render deployment config
```

### Key Files & Their Roles

| File | Purpose | Key Function |
|------|---------|---|
| `whatsapp_app.py` | FastAPI server | Receives WhatsApp messages, routes to agents |
| `router_agent.py` | Message router | Determines if query needs general or RAG response |
| `app.py` | Graph builder | Orchestrates agent workflow using LangGraph |
| `vector_store.py` | FAISS management | Creates, loads, and manages vector database |
| `document_loader.py` | PDF processor | Loads PDFs and splits into chunks |
| `Dockerfile` | Container spec | Defines how app runs in Docker |
| `.dockerignore` | Build filter | Controls what files Docker includes |

---

## 4. RAG System Overview

### What is RAG?

**Retrieval-Augmented Generation** combines:
- **Retrieval**: Search your documents for relevant information
- **Augmentation**: Add that information to the AI prompt
- **Generation**: Let AI generate answer based on your documents

### How It Works in Your System

**Step 1: Document Processing (One-time)**
```
PDF Files → Split into chunks → Create embeddings → Store in FAISS
```

**Step 2: Query Processing (Every user question)**
```
User Query → Create embedding → Search FAISS → Get top matches
          → Send to OpenAI with context → Generate answer
```

### Example

```
User: "What is the adequacy of WHP-01 DCS system?"

System:
  1. Routes to RAG agent
  2. Searches vector DB for "WHP-01 DCS adequacy"
  3. Retrieves relevant chunks from uad_LTDP_adequacy_report.pdf
  4. Sends to OpenAI: "Answer this based on: [document chunks]"
  5. Returns contextualized answer from your documents
```

---

## 5. Deployment Pipeline

### Local Development
```
Code → Local Docker test → Verify functionality
```

### GitHub Repository
```
Git push → Documents + code stored in GitHub
```

### Render Cloud Deployment
```
GitHub push → Render detects → Pulls repo → Builds Docker image
           → Creates container → Initializes vector DB → Deploys
           → Live on https://langgraph-ai-assistant.onrender.com
```

### Full Pipeline Diagram

```
┌──────────────────────────────────────────────────────┐
│  Developer Local Machine                             │
│  - Write code                                        │
│  - Add documents to Agents/data/documents/           │
│  - Test with local Docker                           │
└────────────────┬─────────────────────────────────────┘
                 │
                 ↓ git add . / git commit / git push
┌──────────────────────────────────────────────────────┐
│  GitHub Repository                                   │
│  - Stores code + documents                           │
│  - Webhook configured to notify Render               │
└────────────────┬─────────────────────────────────────┘
                 │
                 ↓ Webhook triggers automatically
┌──────────────────────────────────────────────────────┐
│  Render Build Process                                │
│  1. Clone from GitHub                                │
│  2. Respect .dockerignore (includes documents/,      │
│     excludes vector_db/)                             │
│  3. Build Docker image                               │
│  4. Create container from image                      │
└────────────────┬─────────────────────────────────────┘
                 │
                 ↓ Container starts
┌──────────────────────────────────────────────────────┐
│  Container Initialization                            │
│  1. Load environment variables from .env             │
│  2. Run init_db.py (checks for vector DB)            │
│  3. If not exists: Create from Agents/data/documents/│
│  4. Create embeddings via OpenAI API                 │
│  5. Save FAISS index to disk                         │
│  6. Start Uvicorn server on port 8000                │
└────────────────┬─────────────────────────────────────┘
                 │
                 ↓ Server ready
┌──────────────────────────────────────────────────────┐
│  Running Service                                     │
│  - Listening at: https://langgraph-ai-assistant......│
│  - Ready to receive WhatsApp messages               │
│  - RAG fully functional                             │
└──────────────────────────────────────────────────────┘
```

---

## 6. Key Components Reference

### Router Agent (`router_agent.py`)
- **Function**: Analyzes incoming message
- **Routes to**: 
  - "general" → Use OpenAI for general knowledge
  - "rag" → Query vector database
- **Decision Based On**: Message content analysis

### Vector Store (`rag/vector_store.py`)
- **Functions**:
  - `create_vector_db()` - Creates FAISS index from documents
  - `load_vector_db()` - Loads existing index
  - `retrieve_docs(query)` - Searches relevant documents
- **Storage**: Local FAISS (CPU-based, file-based)

### Document Loader (`rag/document_loader.py`)
- **Loads**: PDF files from `data/documents/`
- **Processing**:
  - Extract text from PDFs
  - Split into chunks (1000 chars, 200 char overlap)
  - Returns as LangChain Document objects

### FastAPI Server (`whatsapp_app.py`)
- **Framework**: FastAPI + Uvicorn
- **Port**: 8000
- **Endpoint**: `POST /whatsapp`
- **Integration**: WhatsApp webhook

---

## 7. Current Issue & Solution Analysis

### Problem Statement

```
ERROR: Document folder not found: /app/Agents/data/documents
Vector DB creation FAILED
RAG functionality NOT available
```

### Root Cause Analysis

**Layer 1: .dockerignore Issue** ❌
- Old: `Agents/data/`  (excludes everything)
- Problem: Excluded documents from Docker image

**Layer 2: GitHub Sync Issue** ❌
- Documents not committed to GitHub
- Render has no source to copy from
- Result: Documents missing in container

### Solution Sequence

**Step 1: Fix .dockerignore** ✅
```
OLD: Agents/data/
NEW: Agents/data/vector_db/
```
**Why**: Allow documents/ but exclude generated vector_db/

**Step 2: Add Documents to GitHub** ⏳
```powershell
git add Agents/data/documents/
git commit -m "Add RAG document files for vector database"
git push origin main
```
**Why**: Render pulls from GitHub, not local machine

**Step 3: Deploy to Render** ⏳
- Manual Deploy with cache clear
- **Why**: Ensures latest code + documents used

**Step 4: Verify Success** ✅
- Watch logs for: `VECTOR DB CREATION SUCCESSFUL`
- Test with WhatsApp query about your documents

### Why This Matters

```
If documents are only local:
  Local Docker works ✓ (has files)
  Render Docker fails ✗ (files not in GitHub)

If documents are in GitHub + .dockerignore fixed:
  Local Docker works ✓
  Render Docker works ✓ (can pull from GitHub)
```

---

## 8. Success Indicators

### Startup Logs (What You Want to See)

```
INFO:rag.vector_store:============================================================
INFO:rag.vector_store:VECTOR DB LOADING STARTED
INFO:rag.vector_store:📁 Looking for Vector DB at: /app/Agents/data/vector_db
INFO:rag.vector_store:📄 Loading documents...
INFO:rag.vector_store:✓ Loaded 45 document chunks
INFO:rag.vector_store:🔑 Creating embeddings...
INFO:rag.vector_store:✓ OpenAI embeddings initialized
INFO:rag.vector_store:🏢 Building FAISS index...
INFO:rag.vector_store:✓ FAISS index built successfully
INFO:rag.vector_store:💾 Saving vector database...
INFO:rag.vector_store:✓ Vector database saved at: /app/Agents/data/vector_db
INFO:rag.vector_store:============================================================
INFO:rag.vector_store:✓✓✓ VECTOR DB CREATION SUCCESSFUL ✓✓✓
INFO:rag.vector_store:============================================================
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Runtime Logs (What Users Experience)

```
Incoming WhatsApp request from [user]
Incoming message: What is ultrasonic flowmeter?
Router selected: rag
✓ Vector DB query executed successfully
Generated answer: [Answer from your documents + AI analysis]
INFO:     [user] - "POST /whatsapp HTTP/1.1" 200 OK
```

### User Experience

- ✅ Assistant responds with context from your documents
- ✅ Answers are specific and accurate
- ✅ No "Document folder not found" errors
- ✅ RAG functionality fully operational

---

## Action Checklist

- [ ] 1. Verify .dockerignore is fixed (Agents/data/vector_db/ only)
- [ ] 2. Add documents to GitHub: `git add Agents/data/documents/`
- [ ] 3. Commit: `git commit -m "Add documents"`
- [ ] 4. Push: `git push origin main`
- [ ] 5. Go to Render Dashboard
- [ ] 6. Click Manual Deploy with cache clear
- [ ] 7. Wait 3-5 minutes for build
- [ ] 8. Check logs for "VECTOR DB CREATION SUCCESSFUL"
- [ ] 9. Test WhatsApp with document-related query
- [ ] 10. Celebrate! 🎉

---

## Technical Notes

### OpenAI API Requirements
- Requires `OPENAI_API_KEY` in .env
- Used for: Embeddings creation, Answer generation
- Costs: Small fees per API call (embeddings + completions)

### FAISS (Facebook AI Similarity Search)
- Vector database library
- Stores document embeddings
- Fast similarity search
- File-based storage (no external service)

### LangChain Integration
- Orchestrates: Document loading, chunking, embeddings
- Manages: Vector store operations, prompts
- Integrates with: OpenAI, FAISS

### Docker Containerization
- Ensures consistent environment across machines
- Eliminates "works on my machine" issues
- Enables easy deployment to cloud (Render)

---

## Troubleshooting Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `Document folder not found` | Documents not in container | Add to GitHub + fix .dockerignore |
| `Vector DB not found` (startup ok) | First run, no existing DB | System creates one automatically |
| `OpenAI API error` | Invalid/missing API key | Check .env file has valid key |
| `FAISS load error` | Corrupted DB file | Delete vector_db/, restart |
| `Uvicorn port already in use` | Port 8000 occupied | Change port or stop conflicting app |

---

## Document Version

**Created**: March 28, 2026  
**Project**: LangGraph AI Assistant  
**Version**: 1.0  
**Status**: Complete with troubleshooting guide

---

## Contact & Support Notes

For questions about:
- **Architecture**: See Application Architecture section
- **Deployment**: See Deployment Pipeline section
- **RAG System**: See RAG System Overview section
- **Issues**: See Troubleshooting Reference section

---

*This document should be reviewed and updated as the project evolves.*
