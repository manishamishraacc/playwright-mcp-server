#!/usr/bin/env python3
"""
Quick test script to verify the MCP server is working
"""

import requests
import json

def test_server():
    base_url = "http://localhost:8000"
    
    print("Testing MCP Server endpoints...")
    print("=" * 40)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    # Test tools endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/tools")
        print(f"✅ Tools endpoint: {response.status_code}")
        tools = response.json()
        print(f"   Available tools: {[tool['name'] for tool in tools]}")
    except Exception as e:
        print(f"❌ Tools endpoint failed: {e}")
    
    # Test a specific tool
    try:
        response = requests.post(
            f"{base_url}/api/v1/tools/create_browser_session/execute",
            json={
                "session_id": "test-session",
                "browser": "chrome",
                "headless": True
            }
        )
        print(f"✅ Create browser session: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Create browser session failed: {e}")

if __name__ == "__main__":
    test_server() 