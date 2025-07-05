"""
FastAPI Main Application - Mindhive AI Chatbot Assessment
=========================================================

Main FastAPI application serving calculator and future API endpoints.

Endpoints:
- /calculator: Mathematical expression evaluation (Phase 3)
- /products: RAG product search (Phase 4)
- /outlets: Text2SQL outlet queries (Phase 4)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
import logging

from .calculator import CalculatorService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Mindhive AI Chatbot API",
    description="API endpoints for calculator, product search, and outlet queries",
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


@app.get("/")
async def root():
    """
    Root endpoint providing API information.
    """
    return {
        "message": "Mindhive AI Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "calculator": "/calculator?expr=<expression>",
            "products": "/products?query=<query> (Phase 4)",
            "outlets": "/outlets?query=<query> (Phase 4)"
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
        "phase": "3-calculator"
    }


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
        - /calculator?expr=15/3 → {"result": 5.0}
        - /calculator?expr=10/0 → {"error": "Division by zero"}
    """
    try:
        logger.info(f"Calculator request: expr='{expr}'")
        
        # Validate and calculate expression
        result = calculator_service.evaluate_expression(expr)
        
        logger.info(f"Calculator result: {result}")
        return {"result": result}
        
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
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 