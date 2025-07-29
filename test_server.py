#!/usr/bin/env python3
"""
Simple test script to verify MCP server functionality
"""

import asyncio
import json
import httpx
import websockets
from typing import Dict, Any

# Server configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/ws"

async def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Health check status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200

async def test_chat_endpoint():
    """Test the chat endpoint"""
    print("\nTesting chat endpoint...")
    async with httpx.AsyncClient() as client:
        payload = {
            "session_id": "test-session-1",
            "message": "Hello, can you run UI tests?",
            "stream": False
        }
        response = await client.post(f"{BASE_URL}/api/v1/chat", json=payload)
        print(f"Chat endpoint status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200

async def test_tools_list():
    """Test the tools list endpoint"""
    print("\nTesting tools list endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/tools")
        print(f"Tools list status: {response.status_code}")
        tools = response.json()
        print(f"Available tools: {[tool['name'] for tool in tools]}")
        return response.status_code == 200

async def test_tool_execution():
    """Test direct tool execution"""
    print("\nTesting tool execution...")
    async with httpx.AsyncClient() as client:
        payload = {
            "browser": "chrome",
            "headless": True,
            "url": "https://example.com",
            "screenshot": False
        }
        response = await client.post(
            f"{BASE_URL}/api/v1/tools/run_ui_tests/execute",
            json=payload
        )
        print(f"Tool execution status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200

async def test_sessions():
    """Test session management"""
    print("\nTesting session management...")
    async with httpx.AsyncClient() as client:
        # List sessions
        response = await client.get(f"{BASE_URL}/api/v1/sessions")
        print(f"Sessions list status: {response.status_code}")
        sessions = response.json()
        print(f"Active sessions: {len(sessions)}")
        return response.status_code == 200

async def test_websocket():
    """Test WebSocket communication"""
    print("\nTesting WebSocket communication...")
    try:
        session_id = "test-ws-session"
        uri = f"{WS_URL}/{session_id}"
        
        async with websockets.connect(uri) as websocket:
            # Send a chat message
            message = {
                "type": "chat",
                "data": {
                    "message": "Get release information for my project"
                }
            }
            await websocket.send(json.dumps(message))
            
            # Listen for responses
            responses = []
            try:
                # Wait for a few responses
                for _ in range(5):
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    responses.append(data)
                    print(f"WebSocket response: {data}")
                    if data.get("type") == "response_end":
                        break
            except asyncio.TimeoutError:
                print("WebSocket timeout - received responses:", len(responses))
            
            return len(responses) > 0
            
    except Exception as e:
        print(f"WebSocket test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("Starting MCP Server tests...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Chat Endpoint", test_chat_endpoint),
        ("Tools List", test_tools_list),
        ("Tool Execution", test_tool_execution),
        ("Session Management", test_sessions),
        ("WebSocket", test_websocket),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
            print(f"✓ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! MCP Server is working correctly.")
    else:
        print("❌ Some tests failed. Check the server logs for details.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 