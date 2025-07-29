import logging
import asyncio
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from schemas.mcp import (
    Message, MessageRole, ToolCall, ToolResult, ToolCallStatus,
    MCPRequest, MCPResponse
)
from context.memory import SessionManager
from registry import ToolRegistry

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base agent class with session context, LLM integration, and tool calling"""
    
    def __init__(self, session_manager: SessionManager, tool_registry: ToolRegistry):
        self.session_manager = session_manager
        self.tool_registry = tool_registry
        self.llm_client = None  # Will be set by subclasses
        
    async def initialize(self):
        """Initialize the agent"""
        logger.info("Initializing base agent")
        # Subclasses should override to initialize LLM client
        
    async def process_request(self, request: MCPRequest) -> MCPResponse:
        """Process an MCP request and return response"""
        try:
            # Ensure session exists
            session = await self.session_manager.get_session(request.session_id)
            if not session:
                await self.session_manager.create_session(request.session_id)
                
            # Add user message to session
            user_message = Message(
                role=MessageRole.USER,
                content=request.message,
                timestamp=datetime.utcnow().isoformat()
            )
            await self.session_manager.add_message(request.session_id, user_message)
            
            # Get conversation history
            messages = await self.session_manager.get_messages(request.session_id, limit=20)
            
            # Generate response with potential tool calls
            response = await self._generate_response(messages, request)
            
            # Execute tool calls if any
            if response.tool_calls:
                tool_results = await self._execute_tool_calls(response.tool_calls)
                
                # Add tool results to session
                tool_message = Message(
                    role=MessageRole.TOOL,
                    content="Tool execution completed",
                    tool_results=tool_results,
                    timestamp=datetime.utcnow().isoformat()
                )
                await self.session_manager.add_message(request.session_id, tool_message)
                
                # Generate final response with tool results
                final_response = await self._generate_final_response(messages, tool_results)
                
                # Add assistant message to session
                assistant_message = Message(
                    role=MessageRole.ASSISTANT,
                    content=final_response.message,
                    timestamp=datetime.utcnow().isoformat()
                )
                await self.session_manager.add_message(request.session_id, assistant_message)
                
                return final_response
            else:
                # Add assistant message to session
                assistant_message = Message(
                    role=MessageRole.ASSISTANT,
                    content=response.message,
                    timestamp=datetime.utcnow().isoformat()
                )
                await self.session_manager.add_message(request.session_id, assistant_message)
                
                return response
                
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return MCPResponse(
                session_id=request.session_id,
                message=f"Error processing request: {str(e)}",
                error=str(e)
            )
            
    async def _generate_response(self, messages: List[Message], request: MCPRequest) -> MCPResponse:
        """Generate initial response with potential tool calls"""
        # This is a placeholder implementation
        # Subclasses should override to integrate with actual LLM
        
        # Simple rule-based tool detection
        user_message = messages[-1].content.lower()
        
        if "test" in user_message and "ui" in user_message:
            # Suggest UI testing tool
            tool_call = ToolCall(
                id=str(uuid.uuid4()),
                name="run_ui_tests",
                arguments={"browser": "chrome", "headless": True}
            )
            return MCPResponse(
                session_id=request.session_id,
                message="I'll run UI tests for you.",
                tool_calls=[tool_call]
            )
        elif "release" in user_message and "info" in user_message:
            # Suggest release info tool
            tool_call = ToolCall(
                id=str(uuid.uuid4()),
                name="get_release_info",
                arguments={"project": "default"}
            )
            return MCPResponse(
                session_id=request.session_id,
                message="I'll get the release information for you.",
                tool_calls=[tool_call]
            )
        else:
            # Default response
            return MCPResponse(
                session_id=request.session_id,
                message="I understand your request. How can I help you further?"
            )
            
    async def _execute_tool_calls(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """Execute tool calls and return results"""
        return await self.tool_registry.execute_tools(tool_calls)
        
    async def _generate_final_response(self, messages: List[Message], tool_results: List[ToolResult]) -> MCPResponse:
        """Generate final response after tool execution"""
        # This is a placeholder implementation
        # Subclasses should override to integrate with actual LLM
        
        # Simple response based on tool results
        if not tool_results:
            return MCPResponse(
                session_id=messages[0].session_id if hasattr(messages[0], 'session_id') else "unknown",
                message="No tools were executed."
            )
            
        # Check for errors
        errors = [result.error for result in tool_results if result.error]
        if errors:
            return MCPResponse(
                session_id=messages[0].session_id if hasattr(messages[0], 'session_id') else "unknown",
                message=f"Some tools failed: {', '.join(errors)}",
                error="Tool execution errors"
            )
            
        # Generate success response
        success_count = len([r for r in tool_results if not r.error])
        return MCPResponse(
            session_id=messages[0].session_id if hasattr(messages[0], 'session_id') else "unknown",
            message=f"Successfully executed {success_count} tool(s)."
        )
        
    async def stream_response(self, request: MCPRequest):
        """Stream response for WebSocket connections"""
        # This is a placeholder for streaming implementation
        # Subclasses should override to provide actual streaming
        
        response = await self.process_request(request)
        
        # Simulate streaming by yielding response parts
        yield {
            "type": "response_start",
            "session_id": request.session_id
        }
        
        # Split response into chunks for streaming
        words = response.message.split()
        for i, word in enumerate(words):
            yield {
                "type": "response_chunk",
                "session_id": request.session_id,
                "content": word + " ",
                "completed": i == len(words) - 1
            }
            await asyncio.sleep(0.1)  # Simulate processing time
            
        yield {
            "type": "response_end",
            "session_id": request.session_id,
            "tool_calls": response.tool_calls
        }
        
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the session"""
        session_info = await self.session_manager.get_session_info(session_id)
        messages = await self.session_manager.get_messages(session_id, limit=10)
        
        return {
            "session_info": session_info,
            "recent_messages": [
                {
                    "role": msg.role,
                    "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in messages[-5:]  # Last 5 messages
            ]
        }
        
    async def clear_session(self, session_id: str) -> bool:
        """Clear a session"""
        return await self.session_manager.delete_session(session_id) 