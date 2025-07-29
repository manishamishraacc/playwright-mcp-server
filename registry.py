import logging
import inspect
from typing import Dict, List, Any, Callable, Optional, Type
from functools import wraps
import asyncio

from schemas.mcp import ToolInfo, ToolCall, ToolResult, ToolCallStatus

logger = logging.getLogger(__name__)

def tool(name: str, description: str = "", parameters: Optional[Dict[str, Any]] = None):
    """Decorator to register a function as a tool"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Tool {name} failed: {e}")
                raise
                
        # Store tool metadata
        wrapper._tool_name = name
        wrapper._tool_description = description
        wrapper._tool_parameters = parameters or {}
        wrapper._tool_func = func
        
        return wrapper
    return decorator

class ToolRegistry:
    """Registry for managing tool functions"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_info: Dict[str, ToolInfo] = {}
        
    async def initialize(self):
        """Initialize the tool registry"""
        logger.info("Initializing tool registry")
        # Tools will be registered via decorators or manual registration
        
    def register_tool(self, func: Callable, name: Optional[str] = None, 
                     description: str = "", parameters: Optional[Dict[str, Any]] = None):
        """Register a function as a tool"""
        tool_name = name or func.__name__
        
        if tool_name in self.tools:
            logger.warning(f"Tool {tool_name} already registered, overwriting")
            
        self.tools[tool_name] = func
        
        # Extract parameter information
        sig = inspect.signature(func)
        param_info = {}
        required_params = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else Any
            param_default = param.default if param.default != inspect.Parameter.empty else None
            
            param_info[param_name] = {
                'type': str(param_type),
                'default': param_default,
                'required': param_default == inspect.Parameter.empty
            }
            
            if param_default == inspect.Parameter.empty:
                required_params.append(param_name)
                
        # Use provided parameters or extracted ones
        final_parameters = parameters or param_info
        
        self.tool_info[tool_name] = ToolInfo(
            name=tool_name,
            description=description or func.__doc__ or "",
            parameters=final_parameters,
            required=required_params
        )
        
        logger.info(f"Registered tool: {tool_name}")
        
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a tool function by name"""
        return self.tools.get(name)
        
    def get_tool_info(self, name: str) -> Optional[ToolInfo]:
        """Get tool information by name"""
        return self.tool_info.get(name)
        
    def list_tools(self) -> List[ToolInfo]:
        """List all registered tools"""
        return list(self.tool_info.values())
        
    def list_tool_names(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())
        
    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call"""
        tool_name = tool_call.name
        tool_func = self.get_tool(tool_name)
        
        if not tool_func:
            return ToolResult(
                call_id=tool_call.id,
                content=None,
                error=f"Tool '{tool_name}' not found"
            )
            
        try:
            # Update tool call status
            tool_call.status = ToolCallStatus.RUNNING
            
            # Execute the tool
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**tool_call.arguments)
            else:
                result = tool_func(**tool_call.arguments)
                
            # Update tool call status
            tool_call.status = ToolCallStatus.COMPLETED
            
            return ToolResult(
                call_id=tool_call.id,
                content=result,
                metadata={'tool_name': tool_name}
            )
            
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            tool_call.status = ToolCallStatus.FAILED
            
            return ToolResult(
                call_id=tool_call.id,
                content=None,
                error=str(e),
                metadata={'tool_name': tool_name}
            )
            
    async def execute_tools(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """Execute multiple tool calls concurrently"""
        if not tool_calls:
            return []
            
        # Execute tools concurrently
        tasks = [self.execute_tool(tool_call) for tool_call in tool_calls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(ToolResult(
                    call_id=tool_calls[i].id,
                    content=None,
                    error=str(result),
                    metadata={'tool_name': tool_calls[i].name}
                ))
            else:
                final_results.append(result)
                
        return final_results
        
    def validate_tool_call(self, tool_call: ToolCall) -> List[str]:
        """Validate a tool call against its schema"""
        errors = []
        tool_info = self.get_tool_info(tool_call.name)
        
        if not tool_info:
            errors.append(f"Tool '{tool_call.name}' not found")
            return errors
            
        # Check required parameters
        for required_param in tool_info.required:
            if required_param not in tool_call.arguments:
                errors.append(f"Required parameter '{required_param}' missing")
                
        # Check parameter types (basic validation)
        for param_name, param_value in tool_call.arguments.items():
            if param_name in tool_info.parameters:
                param_schema = tool_info.parameters[param_name]
                param_type = param_schema.get('type', 'any')
                
                # Basic type checking
                if param_type == 'str' and not isinstance(param_value, str):
                    errors.append(f"Parameter '{param_name}' should be string")
                elif param_type == 'int' and not isinstance(param_value, int):
                    errors.append(f"Parameter '{param_name}' should be integer")
                elif param_type == 'bool' and not isinstance(param_value, bool):
                    errors.append(f"Parameter '{param_name}' should be boolean")
                    
        return errors 