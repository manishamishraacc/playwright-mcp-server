#!/bin/bash

# Startup script for Azure App Service
# This script is used by Azure App Service to start the application

echo "🚀 Starting Playwright MCP Server..."

# Install Playwright browsers if not already installed
if [ ! -d "/home/site/wwwroot/.cache/ms-playwright" ]; then
    echo "📦 Installing Playwright browsers..."
    playwright install --with-deps chromium firefox webkit
fi

# Start the FastAPI application
echo "🌐 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 