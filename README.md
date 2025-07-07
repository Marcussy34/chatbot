# Mindhive AI Chatbot Engineer Assessment

This project is a technical submission for the **AI Chatbot Engineer** role at **Mindhive**. It showcases a LangChain-based chatbot agent capable of multi-turn conversation, agentic planning, tool/API integration, custom RAG pipelines, and robust error handling.

---

## 🧠 Architecture Overview

The system consists of:

- `LangChain agent` with memory and planner/controller logic
- `FastAPI backend` exposing:
  - `/calculator` for arithmetic tool calling
  - `/products` for product-KB RAG retrieval
  - `/outlets` for outlet info via Text2SQL
- `Vector Store (FAISS)` for retrieval
- `SQLite + SQLAlchemy` for outlet data
- `Pytest` test suite for all happy and unhappy paths

---

## ✅ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/mindhive-chatbot
cd mindhive-chatbot
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run FastAPI server

```bash
uvicorn app.main:app --reload
```

### 5. Test the chatbot

```bash
python chatbot/memory_bot.py
```

---

## 🚀 **Deployment to Google Cloud Run**

The application is production-ready and can be deployed to Google Cloud Run:

### **Quick Deployment**
```bash
# 1. Edit deploy.sh and set your PROJECT_ID
nano deploy.sh
# Set: PROJECT_ID="your-google-cloud-project-id"

# 2. Deploy
./deploy.sh
```

### **Manual Steps**
See detailed instructions in [`DEPLOYMENT.md`](DEPLOYMENT.md)

### **Features**
- ✅ **Container-ready**: Multi-stage Docker build
- ✅ **Auto-scaling**: 0-10 instances based on load
- ✅ **Cost-effective**: Pay only when used
- ✅ **Production-grade**: Health checks, monitoring, security
- ✅ **CI/CD ready**: Cloud Build integration

---

## 📂 Project Structure

```
mindhive-chatbot/
├── app/                # FastAPI API server
│   ├── main.py         # Entry point
│   ├── calculator.py   # Calculator endpoint
│   ├── products.py     # RAG product endpoint
│   ├── outlets.py      # Text2SQL outlet endpoint
│   ├── ingestion.py    # FAISS ingestion script
│   ├── db.sqlite       # SQLite DB for outlets
│   ├── schema.sql      # DB schema for reference
├── chatbot/            # LangChain agent logic
│   ├── memory_bot.py   # Multi-turn conversation bot
│   ├── planner.py      # Action planner/controller
│   ├── tools.py        # Tool wrappers for LangChain
├── tests/              # Pytest test suite
├── requirements.txt
├── README.md
```

---

## 🧩 Part 1: Sequential Conversation (State Tracking)

### ✅ Goal

Track multi-turn user conversations using memory.

### ✅ Implementation

- Used `ConversationChain` from LangChain.
- Attached `ConversationBufferMemory` for slot tracking.
- Simulated scenario:
  - User: “Is there an outlet in PJ?”
  - Bot: “Yes! Which outlet?”
  - User: “SS2, what’s the time?”
  - Bot: “SS2 outlet opens at 9AM.”

### ✅ Test Coverage

- `tests/test_memory.py` checks for preserved state across turns.
- Validates memory and follow-up response correctness.

---

## 🧠 Part 2: Agentic Planning (Planner Logic)

### ✅ Goal

Build a planner that determines next steps (ask, act, or end).

### ✅ Implementation

- `planner.py` analyzes input + memory:
  - If incomplete → ask follow-up
  - If math → call `/calculator`
  - If product query → call `/products`
  - If outlet info → call `/outlets`

### ✅ Deliverables

- `chatbot/planner.py` contains the decision function.
- Short logic explanation included in comments.

---

## 🧮 Part 3: Tool Calling (Calculator API)

### ✅ Goal

Perform simple math via calculator API with error handling.

### ✅ Implementation

- `/calculator?expr=2+3` endpoint in FastAPI (`calculator.py`)
- Integrated into LangChain using `Tool` wrapper
- Graceful failure for:
  - Malformed input
  - Division by zero

### ✅ Example

```bash
GET /calculator?expr=10/2
→ {"result": 5}
```

### ✅ Tests

- `tests/test_calculator.py` covers:
  - Valid math
  - Invalid expressions
  - Missing query param

---

## 🔌 Part 4: Custom API + RAG Integration

### 4.1 `/products` - Retrieval-Augmented Generation

#### ✅ Goal

Ingest product data and return AI-generated answers.

#### ✅ Implementation

- Scraped Drinkware product info from [ZUS Shop](https://shop.zuscoffee.com/)
- Stored in FAISS vector store using LangChain
- `/products?query=...` endpoint uses retriever + LLM

#### ✅ Example

```bash
GET /products?query=What’s the best ZUS tumbler?
→ Returns AI summary based on top-k products
```

#### ✅ Test

- `tests/test_rag.py` validates vector search & response

---

### 4.2 `/outlets` - Text2SQL

#### ✅ Goal

Answer natural language outlet queries using SQL.

#### ✅ Implementation

- SQLite DB with columns: `location`, `name`, `hours`, `services`
- LangChain Text2SQLChain to convert user queries → SQL
- `/outlets?query=...` endpoint translates and executes

#### ✅ Example

```bash
GET /outlets?query=What time does SS2 open?
→ Returns "SS2 outlet opens at 9AM"
```

#### ✅ Test

- `tests/test_outlets.py` validates SQL generation & output

---

## ❌ Part 5: Unhappy Flows (Error Handling)

### ✅ Goal

Handle:
- Missing input
- API downtime
- Malicious payloads

### ✅ Implementation

- Checked for:
  - Empty `/calculator?expr=`
  - Forced HTTP 500 using monkeypatch
  - SQL injection attempt in `/outlets`

### ✅ Bot Behavior

- Returns fallback responses like:
  - “Sorry, I didn’t catch that.”
  - “There was a system error. Please try again.”

### ✅ Test Cases

- `tests/test_unhappy.py`

---

## 📄 API Documentation

### `/calculator`

| Method | Path            | Params      | Returns         |
|--------|-----------------|-------------|-----------------|
| GET    | `/calculator`   | `expr=str`  | `{result}` or 400 |

---

### `/products`

| Method | Path         | Params      | Returns             |
|--------|--------------|-------------|---------------------|
| GET    | `/products`  | `query=str` | AI-generated answer |

---

### `/outlets`

| Method | Path        | Params      | Returns       |
|--------|-------------|-------------|---------------|
| GET    | `/outlets`  | `query=str` | SQL + results |

---

## 🌐 Hosted Demo

🟢 **Production Deployment**: Ready for Google Cloud Run deployment

Use the deployment guide in `DEPLOYMENT.md` to deploy to Cloud Run:

```bash
# Quick deployment
./deploy.sh

# Local testing with Docker
./deploy.sh test-local
```

API Testing:
```bash
curl http://localhost:8000/calculator?expr=4*5
curl "http://localhost:8000/products?query=black+tumbler"  
curl "http://localhost:8000/outlets?query=outlets+in+PJ"
```

---

## 📦 Project Directory

```
chatbot/
├── app/                    # FastAPI application
│   ├── main.py             # FastAPI app entry point
│   ├── calculator.py       # Calculator service
│   ├── rag_service.py      # RAG product search
│   ├── sql_service.py      # Text2SQL outlet queries
│   └── __init__.py
├── chatbot/                # LangChain agent logic
│   ├── memory_bot.py       # Multi-turn conversation bot
│   ├── planner.py          # Agentic planner/controller
│   ├── tools.py            # Tool wrappers for LangChain
│   └── __init__.py
├── data/                   # Application data
│   ├── product_index.faiss # FAISS vector index
│   ├── zus_outlets.db      # SQLite outlet database
│   ├── zus_outlets.json    # Outlet data (JSON)
│   └── zus_products.json   # Product data (JSON)
├── scripts/                # Data ingestion scripts
│   ├── scrape_outlets.py   # Outlet data scraper
│   └── scrape_products.py  # Product data scraper
├── tests/                  # Test suite
│   ├── test_memory.py      # Memory/state tests
│   ├── test_calculator.py  # Calculator tests
│   ├── test_planner.py     # Planner tests
│   └── test_phase5_unhappy_flows.py  # Error handling
├── demo_phase*.py          # Phase demonstration scripts
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Local container testing
├── deploy.sh               # Cloud Run deployment script
├── cloudbuild.yaml         # Google Cloud Build config
├── DEPLOYMENT.md           # Deployment documentation
└── README.md               # This file
```