from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

class MessageRole(str, Enum):
    """Message roles for MCP communication"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

class ToolCallStatus(str, Enum):
    """Tool call execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ToolCall(BaseModel):
    """Tool call request model"""
    id: str = Field(..., description="Unique tool call identifier")
    name: str = Field(..., description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    status: ToolCallStatus = Field(default=ToolCallStatus.PENDING, description="Tool call status")

class ToolResult(BaseModel):
    """Tool call result model"""
    call_id: str = Field(..., description="Tool call identifier")
    content: Any = Field(..., description="Tool execution result")
    error: Optional[str] = Field(None, description="Error message if tool failed")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class Message(BaseModel):
    """Message model for conversation"""
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="Tool calls in this message")
    tool_results: Optional[List[ToolResult]] = Field(None, description="Tool results in this message")
    timestamp: Optional[str] = Field(None, description="Message timestamp")

class MCPRequest(BaseModel):
    """MCP request model"""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="User message")
    stream: bool = Field(default=False, description="Whether to stream response")
    tools: Optional[List[str]] = Field(None, description="Available tools for this request")

class MCPResponse(BaseModel):
    """MCP response model"""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="Assistant response")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="Tool calls to execute")
    completed: bool = Field(default=True, description="Whether response is complete")
    error: Optional[str] = Field(None, description="Error message if any")

class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str = Field(..., description="Session identifier")
    created_at: str = Field(..., description="Session creation timestamp")
    message_count: int = Field(..., description="Number of messages in session")
    last_activity: str = Field(..., description="Last activity timestamp")

class ToolInfo(BaseModel):
    """Tool information model"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters schema")
    required: List[str] = Field(default_factory=list, description="Required parameters")

class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    session_id: Optional[str] = Field(None, description="Session identifier") 