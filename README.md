# Mindhive AI Chatbot Engineer Assessment

A production-ready conversational AI chatbot implementing all 5 phases of the Mindhive assessment with advanced RAG, Text2SQL, and tool orchestration capabilities.

## 🌐 **Live Demo**

**Production URL**: https://mindhive-chatbot-yvsu2loedq-uc.a.run.app  
**API Documentation**: https://mindhive-chatbot-yvsu2loedq-uc.a.run.app/docs

## 🚀 **Quick Test**

Try these working examples:
- **Calculator**: [2+3*4](https://mindhive-chatbot-yvsu2loedq-uc.a.run.app/calculator?expr=2%2B3*4)
- **Product Search**: [Find ceramic mugs](https://mindhive-chatbot-yvsu2loedq-uc.a.run.app/products?query=ceramic+mug)
- **Outlet Query**: [Outlets in PJ](https://mindhive-chatbot-yvsu2loedq-uc.a.run.app/outlets?query=outlets+in+Petaling+Jaya)

## 📋 **Implementation Overview**

### **✅ Phase 1: Basic Calculator**
- Safe mathematical expression evaluation using AST parsing
- FastAPI endpoint with comprehensive error handling
- Security measures against code injection

### **✅ Phase 2: LangChain Integration**
- Memory-enabled conversational chatbot
- LangChain framework with OpenAI GPT models
- Persistent conversation history

### **✅ Phase 3: Tool Integration**
- Calculator tool integrated with LangChain
- Dynamic tool selection and orchestration
- Seamless conversation-to-calculation flow

### **✅ Phase 4: RAG Implementation**
- **Vector Store**: FAISS with 200+ ZUS Coffee drinkware products
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **Text2SQL**: Natural language queries to SQLite outlet database
- **Smart Search**: Semantic product recommendations

### **✅ Phase 5: Advanced Conversational AI**
- **Planning & Reasoning**: Multi-step conversation handling
- **Intent Classification**: Dynamic tool selection based on user intent
- **Memory Integration**: Context-aware responses across turns
- **Error Handling**: Comprehensive unhappy path management

---

## 🛠️ **Setup & Run Instructions**

### **Prerequisites**
- Python 3.11+
- OpenAI API Key
- Git

### **Local Development Setup**

1. **Clone the repository**
   ```bash
   git clone https://github.com/Marcussy34/chatbot.git
   cd chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export PORT=8000  # Optional, defaults to 8000
   ```

5. **Run the application**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### **Docker Setup**

1. **Build the image**
   ```bash
   docker build -t mindhive-chatbot .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 -e OPENAI_API_KEY="your-api-key" mindhive-chatbot
   ```

### **Cloud Deployment (Google Cloud Run)**

1. **Prerequisites**
   ```bash
   # Install Google Cloud CLI and authenticate
   gcloud auth login
   gcloud config set project your-project-id
   ```

2. **Deploy**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

### **Running Tests**

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_calculator.py -v
python -m pytest tests/test_memory.py -v
python -m pytest tests/test_planner.py -v
```

---

## 🏗️ **Architecture Overview**

### **System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   LangChain     │    │   Data Layer    │
│   Web Server    │    │   Chatbot       │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Calculator    │    │ • Memory Bot    │    │ • FAISS Vector  │
│ • Products API  │◄──►│ • Planner Bot   │◄──►│ • SQLite DB     │
│ • Outlets API   │    │ • Tool Manager  │    │ • Embeddings    │
│ • Health Check  │    │ • Conversation  │    │ • Product Data  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Component Breakdown**

#### **1. FastAPI Web Server (`app/`)**
- **`main.py`**: API endpoints and routing
- **`calculator.py`**: Safe mathematical expression evaluation
- **`rag_service.py`**: Vector search and product recommendations
- **`sql_service.py`**: Text2SQL outlet queries
- **Features**: Async/await, automatic API docs, input validation

#### **2. LangChain Chatbot (`chatbot/`)**
- **`memory_bot.py`**: Conversation memory management
- **`planner.py`**: Intent classification and action planning
- **`tools.py`**: Tool integration and orchestration
- **Features**: GPT-4 integration, persistent memory, tool selection

#### **3. Data Layer (`data/`)**
- **`product_index.faiss`**: Vector embeddings for 200+ products
- **`zus_outlets.db`**: SQLite database with outlet information
- **`zus_products.json`**: Product catalog for vector search
- **Features**: Efficient similarity search, structured queries

### **Data Flow**

1. **User Input** → FastAPI endpoint or chatbot interface
2. **Intent Classification** → Planner determines action type
3. **Tool Selection** → Calculator, RAG search, or SQL query
4. **Data Processing** → Vector similarity or SQL execution
5. **Response Generation** → LangChain formats natural language response
6. **Memory Update** → Conversation context preserved for future turns

---

## ⚖️ **Key Trade-offs**

### **Framework Choices**

**FastAPI vs Django/Flask**
- ✅ **Chose FastAPI**: Automatic API docs, async support, type hints
- ❌ **Trade-off**: Less ecosystem than Django, newer framework

**LangChain vs Custom Implementation**
- ✅ **Chose LangChain**: Rapid development, memory management, tool integration
- ❌ **Trade-off**: Additional dependency, potential version conflicts

### **Data Storage**

**FAISS vs Pinecone/Weaviate**
- ✅ **Chose FAISS**: No external dependencies, fast local search, cost-effective
- ❌ **Trade-off**: No cloud scaling, manual index management

**SQLite vs PostgreSQL/MySQL**
- ✅ **Chose SQLite**: Zero configuration, portable, perfect for demo
- ❌ **Trade-off**: Limited concurrency, not suitable for high-scale production

### **Deployment**

**Google Cloud Run vs Heroku/Vercel**
- ✅ **Chose Cloud Run**: Serverless scaling, container support, pay-per-use
- ❌ **Trade-off**: Cold starts, Google Cloud complexity

**Multi-stage Docker vs Single Stage**
- ✅ **Chose Multi-stage**: Smaller production image, security, optimization
- ❌ **Trade-off**: More complex build process, longer build times

### **Performance vs Complexity**

**Embeddings Model**
- ✅ **all-MiniLM-L6-v2**: Good balance of speed and accuracy
- ❌ **Trade-off**: Not as accurate as larger models, English-only

**Memory Strategy**
- ✅ **In-memory conversation buffer**: Simple, fast access
- ❌ **Trade-off**: Lost on restart, limited scalability

**Security vs Usability**
- ✅ **AST-based expression evaluation**: Safe from code injection
- ❌ **Trade-off**: Limited mathematical functions, complexity

---

## 📚 **API Specification**

### **Endpoints**

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `GET` | `/health` | Service health check | `{"status": "healthy"}` |
| `GET` | `/calculator` | Mathematical expression evaluation | `?expr=2%2B3` |
| `GET` | `/products` | RAG product search | `?query=ceramic+mug` |
| `GET` | `/outlets` | Text2SQL outlet queries | `?query=outlets+in+PJ` |
| `GET` | `/docs` | Interactive API documentation | Swagger UI |

### **Calculator API**
```json
GET /calculator?expr=2%2B3*4

Response:
{
  "expression": "2+3*4", 
  "result": 14,
  "safe": true
}
```

### **Products API (RAG)**
```json
GET /products?query=black+tumbler

Response:
{
  "query": "black tumbler",
  "products": [
    {
      "name": "ZUS Coffee Black Tumbler 450ml",
      "description": "Sleek black stainless steel tumbler...",
      "price": "RM 45.00",
      "similarity_score": 0.89
    }
  ],
  "total_results": 3
}
```

### **Outlets API (Text2SQL)**
```json
GET /outlets?query=outlets+in+Petaling+Jaya

Response:
{
  "query": "outlets in Petaling Jaya",
  "sql_generated": "SELECT * FROM outlets WHERE area LIKE '%Petaling Jaya%'",
  "outlets": [
    {
      "name": "ZUS Coffee SS2",
      "area": "Petaling Jaya",
      "address": "47300 Petaling Jaya, Selangor",
      "opening_hours": "Monday - Sunday: 7:00 AM - 10:00 PM"
    }
  ],
  "total_results": 2
}
```

---

## 🧪 **Testing Strategy**

### **Test Coverage**
- **Unit Tests**: Core service functionality
- **Integration Tests**: API endpoint validation
- **Security Tests**: Input validation and injection protection
- **Memory Tests**: Conversation persistence
- **Planning Tests**: Intent classification accuracy

### **Test Execution**
```bash
# Run all tests
python -m pytest tests/ -v

# Test results: 76+ passing tests covering all major functionality
```

---

## 🔒 **Security Measures**

- **Input Validation**: All user inputs sanitized
- **Safe Evaluation**: AST-based expression parsing prevents code injection
- **SQL Injection Protection**: Parameterized queries and input filtering
- **Container Security**: Non-root user execution
- **Dependency Management**: Regular security updates

---

## 📁 **Project Structure**

```
chatbot/
├── app/                    # FastAPI Web Application
│   ├── main.py            # API endpoints and routing
│   ├── calculator.py      # Mathematical expression service
│   ├── rag_service.py     # Vector search and RAG implementation
│   └── sql_service.py     # Text2SQL outlet queries
├── chatbot/               # LangChain Chatbot Implementation
│   ├── memory_bot.py      # Conversation memory management
│   ├── planner.py         # Intent classification and planning
│   └── tools.py           # Tool integration and orchestration
├── data/                  # Data Layer
│   ├── product_index.faiss # Vector embeddings for products
│   ├── zus_outlets.db     # SQLite outlet database
│   └── zus_products.json  # Product catalog
├── tests/                 # Comprehensive Test Suite
│   ├── test_calculator.py # Calculator service tests
│   ├── test_memory.py     # Memory and conversation tests
│   └── test_planner.py    # Planning and intent tests
├── Dockerfile             # Production container configuration
├── deploy.sh              # Google Cloud Run deployment script
├── cloudbuild.yaml        # CI/CD pipeline configuration
├── requirements.txt       # Python dependencies
├── README.md              # This documentation
└── SUBMISSION.md          # Formal submission document
```

---

## 🎯 **Submission Summary**

This chatbot demonstrates advanced conversational AI capabilities through:

- **✅ Complete Implementation**: All 5 phases with production deployment
- **✅ Advanced Features**: RAG, Text2SQL, tool orchestration, memory
- **✅ Production Ready**: Security, testing, monitoring, scalability
- **✅ Professional Quality**: Clean code, documentation, architecture

**Live Demo**: https://mindhive-chatbot-yvsu2loedq-uc.a.run.app  
**GitHub Repository**: https://github.com/Marcussy34/chatbot

---

## 📞 **Contact**

For questions about this implementation, please contact the repository owner.