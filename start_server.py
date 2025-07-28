#!/usr/bin/env python3
"""
Startup script for Trakr Backend Server
"""

import uvicorn
import os
from app.core.config import get_settings

def main():
    """Start the FastAPI server"""
    settings = get_settings()
    
    print("🚀 Starting Trakr Backend Server...")
    print(f"📊 Server will be available at: http://localhost:8000")
    print(f"📚 API Documentation will be available at: http://localhost:8000/docs")
    print(f"🔧 Health check endpoint: http://localhost:8000/health")
    print(f"📈 Metrics endpoint: http://localhost:8000/metrics")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 