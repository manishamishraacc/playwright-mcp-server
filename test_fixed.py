#!/usr/bin/env python3
"""
Test script for the fixed server
"""

import requests
import json

def test_fixed_server():
    base_url = "http://localhost:8002"
    
    print("Testing Fixed MCP Server endpoints...")
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
    
    # Test test endpoint
    try:
        response = requests.get(f"{base_url}/test")
        print(f"✅ Test endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Test endpoint failed: {e}")

if __name__ == "__main__":
    test_fixed_server() 