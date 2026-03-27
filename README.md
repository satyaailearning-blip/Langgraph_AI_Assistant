# LangGraph AI Assistant

A Python-based WhatsApp AI agent that uses LangGraph, LangChain, and OpenAI to answer questions from uploaded documents via RAG (Retrieval-Augmented Generation).

## 🎯 Features

- **RAG Agent**: Retrieves answers from uploaded PDF documents
- **Smart Routing**: Automatically routes queries to RAG or general AI agent
- **WhatsApp Integration**: Connected via Twilio for real-time messaging
- **FastAPI Backend**: High-performance REST API
- **Cloudflare Tunnel**: Public HTTPS access without port forwarding
- **Docker Ready**: Containerized for easy deployment
- **Vector Database**: FAISS for efficient document embedding search

---

## 🏗️ Architecture

```
┌─────────────────┐
│   WhatsApp User │
│    (Twilio)     │
└────────┬────────┘
         │
    HTTP POST
         │
    ┌────▼─────────────────────┐
    │   FastAPI App            │
    │  (whatsapp_app.py)       │
    └────┬─────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │   LangGraph Workflow           │
    │   (graph_builder.py)           │
    └────┬───────────────────────────┘
         │
    ┌────▼────────────────┐
    │   Router Agent      │
    │ (router_agent.py)   │
    └────┬────────┬───────┘
         │        │
    ┌────▼──┐  ┌──▼──────────┐
    │General│  │ RAG Agent    │
    │Agent  │  │ (Search Docs)│
    └───────┘  └──┬───────────┘
                  │
            ┌─────▼──────────┐
            │ Vector Database│
            │  (FAISS)       │
            │ + PDFs         │
            └────────────────┘
```

---

## 📦 Project Structure

```
Langgraph_AI_Assistant/
├── Agents/
│   ├── app.py                 # Streamlit UI (optional)
│   ├── main.py                # CLI mode
│   ├── test_agent.py          # Local testing
│   ├── whatsapp_app.py        # FastAPI WhatsApp webhook
│   ├── graph_builder.py       # LangGraph workflow definition
│   ├── router_agent.py        # Query router logic
│   ├── requirements.txt        # Python dependencies
│   ├── dockerfile             # Docker container config
│   ├── .env                   # Environment variables (API keys)
│   ├── rag/
│   │   ├── document_loader.py # PDF loading
│   │   ├── vector_store.py    # FAISS database
│   │   └── __pycache__/
│   ├── data/
│   │   ├── documents/         # Upload PDFs here
│   │   └── vector_db/         # FAISS index (auto-generated)
│   └── venv/                  # Python virtual environment
├── requirements.txt           # Root requirements (same as Agents/)
├── dockerfile                 # Docker config (deprecated)
├── .dockerignore             # Docker build exclusions
└── README.md                 # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop (optional, for containerized deployment)
- OpenAI API key
- Twilio account (for WhatsApp integration)

### 1. Clone & Setup

```bash
cd Langgraph_AI_Assistant
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### 2. Configure Environment

Create `Agents/.env`:
```env
OPENAI_API_KEY=your-openai-api-key-here
PYTHONPATH=/app
```

### 3. Upload Documents

Add PDF files to `Agents/data/documents/`:
```
Agents/data/documents/
├── FEED_SOW_IA1234.pdf
├── uad_ltdp2_sow.pdf
└── uad_LTDP_adequacy_report.pdf
```

### 4. Build Vector Database

```powershell
cd Agents
python -c "from rag.vector_store import create_vector_db; create_vector_db()"
```

### 5. Run Locally

**Option A: FastAPI (WhatsApp ready)**
```powershell
cd Agents
python -m uvicorn whatsapp_app:app --host 0.0.0.0 --port 8000
```

**Option B: CLI Testing**
```powershell
cd Agents
python test_agent.py
# > Ask your question: What is the pipe class of Tag 265BDV230100?
```

**Option C: Streamlit UI**
```powershell
cd Agents
streamlit run app.py
```

### 6. Test Query

```powershell
# RAG Query (searches documents)
curl -X POST http://localhost:8000/whatsapp `
  -d "Body=What is the scope of UAD LTDP-2?" `
  -H "Content-Type: application/x-www-form-urlencoded"

# General Query (uses OpenAI general knowledge)
curl -X POST http://localhost:8000/whatsapp `
  -d "Body=What is Python?" `
  -H "Content-Type: application/x-www-form-urlencoded"
```

---

## 🐳 Docker Deployment

### Build Image

```powershell
docker build --no-cache -t langgraph-ai-assistant -f .\Agents\Dockerfile .
```

### Run Container

```powershell
docker run -d -p 8000:8000 `
  --env-file Agents\.env `
  --name langgraph-bot `
  langgraph-ai-assistant
```

### Check Logs

```powershell
docker logs langgraph-bot -f
```

### Stop Container

```powershell
docker stop langgraph-bot
docker rm langgraph-bot
```

---

## 🌐 Cloudflare Tunnel Setup

For public WhatsApp access without port forwarding:

```powershell
cloudflared tunnel --url http://localhost:8000 --protocol http2
```

Output:
```
https://your-tunnel-url.trycloudflare.com → http://localhost:8000
```

Use this URL in Twilio webhook configuration.

---

## 📱 Twilio WhatsApp Integration

1. **Go to**: https://www.twilio.com/console/sms/whatsapp/
2. **Create WhatsApp Sender**: Request a WhatsApp Business phone number
3. **Configure Webhook**:
   - Webhook URL: `https://your-cloudflare-url/whatsapp`
   - Method: `POST`
4. **Test**: Send a message to your WhatsApp number
5. **Monitor Logs**: Watch `docker logs` for incoming messages

---

## 🤖 How RAG Works

### Router Agent Logic
The router categorizes queries based on keywords:

**RAG Keywords** (searches documents):
- `tag`, `datasheet`, `sow`, `specification`, `site survey`
- `observations`, `dcs`, `esd`, `fgs`, `whp` 
- `cpp`, `platform`, `wellhead`, `instrument`, `icss`
- `modbus`, `cabinet`, `panel`, `project`, `uad`, `ltdp`

**General Keywords** (uses OpenAI):
- Everything else → OpenAI general knowledge

### Vector Database Flow
1. **Load PDFs** → Split into 1000-char chunks with 200-char overlap
2. **Embed** → OpenAI embeddings (ada-002)
3. **Store** → FAISS index saved locally
4. **Search** → Similarity search retrieves top 3 chunks
5. **Combine** → Context + Question → LLM answer

---

## 🔧 Configuration

### `graph_builder.py`
- Edit RAG keywords in `route_question()`
- Change LLM model: `ChatOpenAI(model="gpt-4o-mini")`

### `rag/vector_store.py`
- Chunk size: `chunk_size=1000`
- Chunk overlap: `chunk_overlap=200`
- Search results: `k=3` (top 3 documents)

### `whatsapp_app.py`
- Max response length: 1500 chars
- Port: 8000 (configurable in Dockerfile)

---

## 📊 Monitoring

### Docker Stats
```powershell
docker stats langgraph-bot
```

### Check If Service Is Running
```powershell
curl http://localhost:8000/
# Expected: {"status":"WhatsApp AI Assistant is running"}
```

### View Recent Queries
```powershell
docker logs langgraph-bot --tail 50
```

Look for:
```
Router selected: rag     # Document search
Router selected: general # General AI
```

---

## 🛠️ Troubleshooting

### Error: `ModuleNotFoundError: No module named 'graph_builder'`
**Solution**: Ensure `PYTHONPATH=/app` is set in Dockerfile and sys.path is updated

### Error: `No module named 'Agents'`
**Solution**: Run from `Agents/` folder or use absolute imports

### Error: `Vector DB not found`
**Solution**: Run `create_vector_db()` after adding PDFs

### Port 8000 already in use
**Solution**: 
```powershell
netstat -ano | findstr :8000
Stop-Process -Id <PID> -Force
```

### Docker won't connect to port
**Solution**: Ensure Docker Desktop is running and port is free

---

## 📝 Advanced Usage

### Add New Documents
```powershell
1. Add PDFs to Agents/data/documents/
2. Run: python -c "from rag.vector_store import create_vector_db; create_vector_db()"
3. Restart server/container
```

### Customize Router Keywords
Edit `Agents/router_agent.py`:
```python
rag_keywords = [
    "your", "custom", "keywords", "here"
]
```

### Change LLM Model
Edit `Agents/graph_builder.py`:
```python
llm = ChatOpenAI(model="gpt-4-turbo")  # Switch model
```

### Use Different Vector Store
Replace FAISS with Pinecone, Weaviate, etc. in `rag/vector_store.py`

---

## 📋 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/whatsapp` | POST | WhatsApp webhook (Twilio) |

### POST `/whatsapp`
**Parameters:**
- `Body` (string): User message from WhatsApp

**Response:**
- XML Twilio response with bot answer

---

## 🔐 Security

- ✅ API keys stored in `.env` (never commit)
- ✅ Cloudflare tunnel encrypts traffic
- ✅ Docker isolates dependencies
- ⚠️ Consider rate limiting for Twilio webhook
- ⚠️ Add authentication for production

---

## 📜 Dependencies

See `requirements.txt`:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `langgraph` - Graph-based workflows
- `langchain` - LLM orchestration
- `langchain-openai` - OpenAI integration
- `langchain-community` - FAISS & document loaders
- `pypdf` - PDF parsing
- `faiss-cpu` - Vector similarity search
- `twilio` - WhatsApp integration
- `python-dotenv` - Environment variables
- `streamlit` - UI framework
- `openai` - OpenAI API client

---

## 🚀 Production Checklist

- [ ] Use `gpt-4-turbo` or `gpt-4` for production
- [ ] Set up proper logging (CloudWatch, Sentry)
- [ ] Add rate limiting
- [ ] Use managed vector DB (Pinecone, Weaviate)
- [ ] Deploy on cloud (AWS, GCP, Azure)
- [ ] Set up monitoring & alerts
- [ ] Configure auto-scaling
- [ ] Test failover & disaster recovery
- [ ] Implement caching layer (Redis)
- [ ] Add request validation & sanitization

---

## 💡 Tips

1. **Faster Setup**: Use `pip install -r requirements.txt` instead of installing packages individually
2. **Debug Mode**: Add `print()` statements in `graph_builder.py` to trace flow
3. **Test Locally First**: Use `test_agent.py` before Docker
4. **Monitor Costs**: Track OpenAI API usage in account → Usage
5. **Batch Updates**: Rebuild vector DB once per day, not per query

---

## 🤝 Contributing

To add improvements:
1. Create a feature branch
2. Test locally with `test_agent.py`
3. Build & test Docker image
4. Submit pull request

---

## 📧 Support

For issues:
1. Check Docker logs: `docker logs langgraph-bot`
2. Review error messages in terminal
3. Verify `.env` file has valid API key
4. Confirm PDFs are in `data/documents/`

---

## 📄 License

MIT License - Use freely for commercial & personal projects

---

## 🎓 Learn More

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangChain Docs](https://python.langchain.com/)
- [OpenAI API](https://platform.openai.com/docs)
- [Twilio WhatsApp](https://www.twilio.com/docs/whatsapp)
- [FAISS](https://faiss.ai/)
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-applications/)

---

**Last Updated**: March 26, 2026  
**Version**: 1.0.0
