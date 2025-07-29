#!/usr/bin/env python3
"""
Example client for the MCP Server
Demonstrates HTTP and WebSocket communication
"""

import asyncio
import json
import httpx
import websockets
from typing import Dict, Any

class MCPClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws") + "/api/v1/ws"
        
    async def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            return response.json()
    
    async def chat(self, session_id: str, message: str, stream: bool = False) -> Dict[str, Any]:
        """Send a chat message"""
        async with httpx.AsyncClient() as client:
            payload = {
                "session_id": session_id,
                "message": message,
                "stream": stream
            }
            response = await client.post(f"{self.base_url}/api/v1/chat", json=payload)
            return response.json()
    
    async def list_tools(self) -> list:
        """List available tools"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/v1/tools")
            return response.json()
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool directly"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/tools/{tool_name}/execute",
                json=arguments
            )
            return response.json()
    
    async def list_sessions(self) -> list:
        """List active sessions"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/v1/sessions")
            return response.json()
    
    async def websocket_chat(self, session_id: str, message: str):
        """Chat via WebSocket"""
        uri = f"{self.ws_url}/{session_id}"
        
        async with websockets.connect(uri) as websocket:
            # Send message
            payload = {
                "type": "chat",
                "data": {"message": message}
            }
            await websocket.send(json.dumps(payload))
            
            # Listen for responses
            print(f"WebSocket chat for session {session_id}:")
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    print(f"  {data['type']}: {data.get('content', data)}")
                    
                    if data.get("type") == "response_end":
                        break
                except asyncio.TimeoutError:
                    print("  Timeout waiting for response")
                    break

async def demo_http_api():
    """Demonstrate HTTP API usage"""
    print("=== HTTP API Demo ===")
    client = MCPClient()
    
    # Health check
    health = await client.health_check()
    print(f"Server health: {health}")
    
    # List tools
    tools = await client.list_tools()
    print(f"Available tools: {[tool['name'] for tool in tools]}")
    
    # Chat
    response = await client.chat("demo-session", "Can you run UI tests on my website?")
    print(f"Chat response: {response}")
    
    # Execute tool directly
    tool_result = await client.execute_tool("run_ui_tests", {
        "browser": "chrome",
        "headless": True,
        "url": "https://example.com",
        "screenshot": True
    })
    print(f"Tool execution result: {tool_result}")
    
    # List sessions
    sessions = await client.list_sessions()
    print(f"Active sessions: {len(sessions)}")

async def demo_websocket():
    """Demonstrate WebSocket usage"""
    print("\n=== WebSocket Demo ===")
    client = MCPClient()
    
    # WebSocket chat
    await client.websocket_chat("ws-demo-session", "Get release information for my project")

async def interactive_demo():
    """Interactive demo"""
    print("\n=== Interactive Demo ===")
    client = MCPClient()
    
    session_id = input("Enter session ID (or press Enter for auto-generated): ").strip()
    if not session_id:
        session_id = f"interactive-{asyncio.get_event_loop().time():.0f}"
    
    print(f"Using session: {session_id}")
    
    while True:
        message = input("\nEnter message (or 'quit' to exit): ").strip()
        if message.lower() in ['quit', 'exit', 'q']:
            break
        
        try:
            response = await client.chat(session_id, message)
            print(f"Response: {response['message']}")
            
            if response.get('tool_calls'):
                print(f"Tool calls: {response['tool_calls']}")
        except Exception as e:
            print(f"Error: {e}")

async def main():
    """Main demo function"""
    print("MCP Server Client Demo")
    print("=" * 50)
    
    try:
        # Test server connection
        client = MCPClient()
        health = await client.health_check()
        print(f"Server status: {health.get('status', 'unknown')}")
        
        # Run demos
        await demo_http_api()
        await demo_websocket()
        
        # Interactive demo
        print("\n" + "=" * 50)
        choice = input("Run interactive demo? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            await interactive_demo()
            
    except Exception as e:
        print(f"Error connecting to server: {e}")
        print("Make sure the MCP server is running with: uvicorn main:app --reload")

if __name__ == "__main__":
    asyncio.run(main()) 