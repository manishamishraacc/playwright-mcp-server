#!/usr/bin/env python3
"""
Startup script for Azure App Service
This script handles the startup process for the Playwright MCP Server
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def install_playwright_browsers():
    """Install Playwright browsers if not already installed"""
    try:
        logger.info("Checking Playwright browsers...")
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "--with-deps", "chromium", "firefox", "webkit"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Playwright browsers installed successfully")
        else:
            logger.warning(f"⚠️ Playwright installation warning: {result.stderr}")
    except Exception as e:
        logger.error(f"❌ Error installing Playwright browsers: {e}")

def main():
    """Main startup function"""
    logger.info("🚀 Starting Playwright MCP Server...")
    
    # Install Playwright browsers
    install_playwright_browsers()
    
    # Get port from environment variable
    port = os.environ.get('PORT', '8000')
    
    # Start the FastAPI application
    logger.info(f"🌐 Starting FastAPI server on port {port}...")
    
    try:
        import uvicorn
        from main import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(port),
            log_level="info"
        )
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 