import logging
import json
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import StreamingResponse

from schemas.mcp import (
    MCPRequest, MCPResponse, SessionInfo, ToolInfo, WebSocketMessage
)
from agents.base_agent import BaseAgent
from context.memory import SessionManager
from registry import ToolRegistry

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected for session: {session_id}")
        
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected for session: {session_id}")
            
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to session {session_id}: {e}")
                self.disconnect(session_id)

manager = ConnectionManager()

# Dependency injection
def get_agent() -> BaseAgent:
    """Get the agent instance"""
    # Import here to avoid circular imports
    import sys
    # Try main_fixed first (current running module), then main
    main_module = sys.modules.get('main_fixed') or sys.modules.get('main')
    if main_module:
        return BaseAgent(main_module.session_manager, main_module.tool_registry)
    else:
        # Fallback for testing
        from registry import ToolRegistry
        from context.memory import SessionManager
        return BaseAgent(SessionManager(), ToolRegistry())

def get_session_manager() -> SessionManager:
    """Get the session manager instance"""
    import sys
    # Try main_fixed first (current running module), then main
    main_module = sys.modules.get('main_fixed') or sys.modules.get('main')
    if main_module:
        return main_module.session_manager
    else:
        # Fallback for testing
        from context.memory import SessionManager
        return SessionManager()

def get_tool_registry() -> ToolRegistry:
    """Get the tool registry instance"""
    import sys
    # Try main_fixed first (current running module), then main
    main_module = sys.modules.get('main_fixed') or sys.modules.get('main')
    if main_module:
        return main_module.tool_registry
    else:
        # Fallback for testing
        from registry import ToolRegistry
        return ToolRegistry()

@router.post("/chat", response_model=MCPResponse)
async def chat(
    request: MCPRequest,
    agent: BaseAgent = Depends(get_agent)
):
    """Process a chat request"""
    try:
        response = await agent.process_request(request)
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def chat_stream(
    request: MCPRequest,
    agent: BaseAgent = Depends(get_agent)
):
    """Stream a chat response"""
    async def generate():
        try:
            async for chunk in agent.stream_response(request):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            logger.error(f"Error in stream endpoint: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    agent: BaseAgent = Depends(get_agent)
):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Parse the message
            try:
                ws_message = WebSocketMessage(**message_data)
            except Exception as e:
                await manager.send_message(session_id, {
                    "type": "error",
                    "error": f"Invalid message format: {e}"
                })
                continue
                
            # Handle different message types
            if ws_message.type == "chat":
                await handle_chat_message(session_id, ws_message, agent)
            elif ws_message.type == "ping":
                await manager.send_message(session_id, {"type": "pong"})
            else:
                await manager.send_message(session_id, {
                    "type": "error",
                    "error": f"Unknown message type: {ws_message.type}"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(session_id)

async def handle_chat_message(session_id: str, ws_message: WebSocketMessage, agent: BaseAgent):
    """Handle chat messages over WebSocket"""
    try:
        # Create MCP request
        request = MCPRequest(
            session_id=session_id,
            message=ws_message.data.get("message", ""),
            stream=True
        )
        
        # Send start message
        await manager.send_message(session_id, {
            "type": "response_start",
            "session_id": session_id
        })
        
        # Stream response
        async for chunk in agent.stream_response(request):
            await manager.send_message(session_id, {
                "type": chunk.get("type", "response_chunk"),
                "session_id": session_id,
                **chunk
            })
            
    except Exception as e:
        logger.error(f"Error handling chat message: {e}")
        await manager.send_message(session_id, {
            "type": "error",
            "error": str(e)
        })

@router.get("/sessions", response_model=list[SessionInfo])
async def list_sessions(
    session_manager: SessionManager = Depends(get_session_manager)
):
    """List all active sessions"""
    try:
        return await session_manager.list_sessions()
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get session information"""
    try:
        session_info = await session_manager.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        return session_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Delete a session"""
    try:
        success = await session_manager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools", response_model=list[ToolInfo])
async def list_tools(
    tool_registry: ToolRegistry = Depends(get_tool_registry)
):
    """List all available tools"""
    try:
        return tool_registry.list_tools()
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools/{tool_name}", response_model=ToolInfo)
async def get_tool_info(
    tool_name: str,
    tool_registry: ToolRegistry = Depends(get_tool_registry)
):
    """Get tool information"""
    try:
        tool_info = tool_registry.get_tool_info(tool_name)
        if not tool_info:
            raise HTTPException(status_code=404, detail="Tool not found")
        return tool_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool info for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/{tool_name}/execute")
async def execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    tool_registry: ToolRegistry = Depends(get_tool_registry)
):
    """Execute a tool directly"""
    try:
        from schemas.mcp import ToolCall
        
        # Create tool call
        tool_call = ToolCall(
            id="direct_execution",
            name=tool_name,
            arguments=arguments
        )
        
        # Execute tool
        result = await tool_registry.execute_tool(tool_call)
        
        return {
            "tool_name": tool_name,
            "result": result.content,
            "error": result.error,
            "metadata": result.metadata
        }
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 