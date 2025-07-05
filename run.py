#!/usr/bin/env python3
"""
Production entry point for Render deployment.
Handles PORT environment variable and starts the FastAPI app.
"""

import os
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (Render provides this)
    port = int(os.environ.get("PORT", 8000))
    
    # Start the FastAPI app in production mode
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=port,
        workers=1,  # Single worker for free tier
        log_level="info"
    ) 