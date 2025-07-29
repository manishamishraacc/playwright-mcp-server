#!/usr/bin/env python3
"""
Simple test server to isolate routing issues
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Simple Test Server",
    description="Simple test server",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Simple test server is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Simple server is working"
    }

@app.get("/test")
async def test():
    """Test endpoint"""
    return {
        "message": "Test endpoint working"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "test_simple_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 