"""
FastAPI Main Application - Mindhive AI Chatbot Assessment
=========================================================

Main FastAPI application serving calculator and future API endpoints.

Endpoints:
- /chat: Interactive chatbot with memory and tool integration (Core Feature)
- /calculator: Mathematical expression evaluation (Phase 3)
- /products: RAG product search (Phase 4)
- /outlets: Text2SQL outlet queries (Phase 4)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from typing import Optional, Dict, Any
import logging
import sys
from pathlib import Path

# Add chatbot to path
sys.path.append(str(Path(__file__).parent.parent))

from .calculator import CalculatorService
from .rag_service import create_rag_service
from .sql_service import create_sql_service
from chatbot.planner import PlannerBot
from chatbot.memory_bot import MemoryBot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Mindhive AI Chatbot API",
    description="API endpoints for calculator, product search, outlet queries, and interactive chat",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
calculator_service = CalculatorService()
rag_service = create_rag_service()
sql_service = create_sql_service()

# Initialize chatbot with tool integration
planner_bot = PlannerBot(enable_tools=True)
memory_bot = MemoryBot()

# In-memory conversation storage (for demo purposes)
# In production, use persistent storage like Redis
conversations: Dict[str, Dict[str, Any]] = {}


class ChatMessage(BaseModel):
    """Chat message request model."""
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    session_id: str
    conversation_context: Dict[str, Any]
    planner_decision: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    """
    Root endpoint providing API information.
    """
    return {
        "message": "Mindhive AI Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat (POST) - Interactive chatbot with memory and tools",
            "calculator": "/calculator?expr=<expression>",
            "products": "/products?query=<query>",
            "outlets": "/outlets?query=<query>"
        },
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "chatbot-api",
        "phase": "complete-chatbot",
        "services": {
            "calculator": "available",
            "rag": "available" if rag_service else "unavailable",
            "sql": "available" if sql_service else "unavailable",
            "chatbot": "available",
            "memory": "available",
            "planner": "available"
        }
    }


@app.post("/chat")
async def chat(chat_request: ChatMessage) -> ChatResponse:
    """
    Interactive chatbot endpoint with memory and tool integration.
    
    This endpoint demonstrates the core chatbot functionality including:
    - Conversation memory across multiple turns
    - Intent classification and action planning
    - Tool integration (calculator, product search, outlet queries)
    - Context-aware responses
    
    Args:
        chat_request: Chat message with optional session ID
        
    Returns:
        ChatResponse with bot response and conversation context
        
    Examples:
        POST /chat
        {"message": "Is there an outlet in Petaling Jaya?", "session_id": "user123"}
        
        POST /chat  
        {"message": "SS2, what's the opening time?", "session_id": "user123"}
        
        POST /chat
        {"message": "Calculate 2+3*4", "session_id": "user123"}
    """
    try:
        session_id = chat_request.session_id or "default"
        user_message = chat_request.message.strip()
        
        logger.info(f"Chat request: session={session_id}, message='{user_message}'")
        
        # Initialize session if new
        if session_id not in conversations:
            conversations[session_id] = {
                "planner": PlannerBot(enable_tools=True),
                "memory": MemoryBot(),
                "turn_count": 0
            }
        
        session = conversations[session_id]
        session["turn_count"] += 1
        
        # Get planner decision
        planner_result = session["planner"].execute_conversation_turn(user_message)
        
        # Update memory with the interaction
        memory_response = session["memory"].chat(user_message)
        
        # Prepare response
        bot_response = planner_result.get("response", "I'm not sure how to help with that.")
        
        # Get conversation context
        conversation_context = {
            "turn_count": session["turn_count"],
            "memory_contents": session["memory"].get_memory_contents(),
            "planner_action": planner_result.get("decision", {}).action.value if planner_result.get("decision") else None,
            "planner_confidence": planner_result.get("decision", {}).confidence if planner_result.get("decision") else None
        }
        
        logger.info(f"Chat response: session={session_id}, action={conversation_context.get('planner_action')}")
        
        return ChatResponse(
            response=bot_response,
            session_id=session_id,
            conversation_context=conversation_context,
            planner_decision={
                "action": conversation_context.get('planner_action'),
                "reasoning": planner_result.get("decision", {}).reasoning if planner_result.get("decision") else None,
                "confidence": conversation_context.get('planner_confidence')
            }
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )


@app.get("/chat/sessions")
async def get_active_sessions():
    """
    Get information about active chat sessions.
    
    Returns:
        Dictionary with active session information
    """
    return {
        "active_sessions": list(conversations.keys()),
        "total_sessions": len(conversations),
        "sessions_info": {
            session_id: {
                "turn_count": session["turn_count"],
                "memory_length": len(session["memory"].get_memory_contents()),
            }
            for session_id, session in conversations.items()
        }
    }


@app.delete("/chat/sessions/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a specific chat session.
    
    Args:
        session_id: Session ID to clear
        
    Returns:
        Confirmation message
    """
    if session_id in conversations:
        del conversations[session_id]
        return {"message": f"Session {session_id} cleared successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")


@app.get("/calculator")
async def calculate(
    expr: str = Query(..., description="Mathematical expression to evaluate", example="2+3*4")
):
    """
    Calculate mathematical expressions safely.
    
    Args:
        expr: Mathematical expression (e.g., "2+3", "10*5", "15/3")
        
    Returns:
        JSON with result or error message
        
    Examples:
        - /calculator?expr=2+3 → {"result": 5}
        - /calculator?expr=10*5 → {"result": 50}
        - /calculator?expr=10/0 → {"error": "Division by zero"}
    """
    try:
        logger.info(f"Calculator request: expr='{expr}'")
        
        # Validate and calculate expression
        result = calculator_service.evaluate_expression(expr)
        
        logger.info(f"Calculator result: {result}")
        return {
            "expression": expr,
            "result": result,
            "safe": True
        }
        
    except ValueError as e:
        logger.warning(f"Calculator validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid expression: {str(e)}"
        )
    except ZeroDivisionError:
        logger.warning(f"Calculator division by zero: {expr}")
        raise HTTPException(
            status_code=400,
            detail="Division by zero is not allowed"
        )
    except Exception as e:
        logger.error(f"Calculator unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during calculation"
        )


@app.get("/products")
async def search_products(
    query: str = Query(..., description="Search query for drinkware products", example="black tumbler")
):
    """
    Search drinkware products using RAG (Retrieval-Augmented Generation).
    
    Args:
        query: Natural language search query
        
    Returns:
        JSON with AI-generated summary and relevant products
        
    Examples:
        - /products?query=black tumbler
        - /products?query=ceramic mug for office
        - /products?query=travel bottle
    """
    try:
        logger.info(f"Product search request: query='{query}'")
        
        # Get product recommendations using RAG
        result = rag_service.get_product_recommendations(query)
        
        logger.info(f"Product search result: {result['total_found']} products found")
        return result
        
    except Exception as e:
        logger.error(f"Product search error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during product search"
        )


@app.get("/outlets")
async def query_outlets(
    query: str = Query(..., description="Natural language query for outlet information", example="outlets in SS2")
):
    """
    Query outlet information using Text2SQL.
    
    Args:
        query: Natural language query about outlets
        
    Returns:
        JSON with formatted outlet information
        
    Examples:
        - /outlets?query=outlets in Petaling Jaya
        - /outlets?query=opening hours SS2
        - /outlets?query=phone number KLCC
        - /outlets?query=all outlets
    """
    try:
        logger.info(f"Outlet query request: query='{query}'")
        
        # Process query using Text2SQL
        result = sql_service.query_outlets(query)
        
        # Format for user-friendly response
        formatted_response = sql_service.format_results_for_user(result)
        
        # Return both formatted and raw data
        response = {
            "query": query,
            "sql_generated": result.get('sql_query', ''),
            "outlets": result.get('results', []),
            "total_results": result.get('total_results', 0),
            "formatted_response": formatted_response
        }
        
        logger.info(f"Outlet query result: {result.get('total_results', 0)} outlets found")
        return response
        
    except Exception as e:
        logger.error(f"Outlet query error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during outlet query"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Custom exception handler for consistent error responses.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    General exception handler for unexpected errors.
    """
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )


# Development server
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 