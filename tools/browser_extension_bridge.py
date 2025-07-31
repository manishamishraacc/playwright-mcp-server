import logging
import asyncio
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

from registry import tool

logger = logging.getLogger(__name__)

class BrowserExtensionBridge:
    """Bridge to communicate with browser extensions on client machines"""
    
    def __init__(self):
        self.client_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def register_client(self, client_id: str, client_info: Dict[str, Any]) -> bool:
        """Register a client with browser extension"""
        self.client_sessions[client_id] = {
            "info": client_info,
            "registered_at": datetime.utcnow(),
            "active_sessions": {}
        }
        logger.info(f"Registered client: {client_id}")
        return True
        
    async def send_command_to_client(self, client_id: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send command to specific client's browser extension"""
        if client_id not in self.client_sessions:
            raise Exception(f"Client {client_id} not registered")
            
        # In a real implementation, this would send via WebSocket or HTTP
        # For now, we'll simulate the response
        logger.info(f"Sending command to client {client_id}: {command}")
        
        # Simulate client response
        await asyncio.sleep(0.5)
        
        return {
            "client_id": client_id,
            "command": command,
            "status": "sent",
            "timestamp": datetime.utcnow().isoformat()
        }

# Global bridge instance
extension_bridge = BrowserExtensionBridge()

@tool(
    name="register_browser_extension_client",
    description="Register a browser extension client for remote browser automation",
    parameters={
        "client_id": {
            "type": "str",
            "description": "Unique client identifier",
            "required": True
        },
        "client_info": {
            "type": "dict",
            "description": "Client information (browser type, capabilities, etc.)",
            "default": {}
        }
    }
)
async def register_browser_extension_client(
    client_id: str,
    client_info: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Register a browser extension client for remote browser automation
    
    This allows the MCP server to send browser automation commands to client machines
    where the browser extension is installed.
    """
    
    logger.info(f"Registering browser extension client: {client_id}")
    
    if client_info is None:
        client_info = {
            "browser": "chrome",
            "capabilities": ["browser_automation", "screenshots", "form_filling"],
            "version": "1.0.0"
        }
    
    success = await extension_bridge.register_client(client_id, client_info)
    
    result = {
        "client_id": client_id,
        "client_info": client_info,
        "status": "registered" if success else "failed",
        "registered_at": datetime.utcnow().isoformat(),
        "message": f"Browser extension client {client_id} registered successfully"
    }
    
    logger.info(f"Browser extension client registered: {client_id}")
    
    return result

@tool(
    name="create_remote_browser_session",
    description="Create a browser session on a remote client machine via browser extension",
    parameters={
        "client_id": {
            "type": "str",
            "description": "Client identifier where browser should launch",
            "required": True
        },
        "session_id": {
            "type": "str",
            "description": "Unique session identifier",
            "required": True
        },
        "browser": {
            "type": "str",
            "description": "Browser to use (chrome, firefox, safari)",
            "default": "chrome"
        },
        "headless": {
            "type": "bool",
            "description": "Run browser in headless mode",
            "default": False
        }
    }
)
async def create_remote_browser_session(
    client_id: str,
    session_id: str,
    browser: str = "chrome",
    headless: bool = False
) -> Dict[str, Any]:
    """
    Create a browser session on a remote client machine
    
    This sends a command to the browser extension on the specified client machine
    to launch a new browser session.
    """
    
    logger.info(f"Creating remote browser session: {session_id} on client: {client_id}")
    
    command = {
        "type": "CREATE_BROWSER_SESSION",
        "data": {
            "session_id": session_id,
            "browser": browser,
            "headless": headless
        }
    }
    
    try:
        response = await extension_bridge.send_command_to_client(client_id, command)
        
        result = {
            "client_id": client_id,
            "session_id": session_id,
            "browser": browser,
            "headless": headless,
            "status": "created",
            "created_at": datetime.utcnow().isoformat(),
            "message": f"Remote browser session {session_id} created on client {client_id}",
            "response": response
        }
        
        # Store session info
        if client_id in extension_bridge.client_sessions:
            extension_bridge.client_sessions[client_id]["active_sessions"][session_id] = {
                "browser": browser,
                "headless": headless,
                "created_at": datetime.utcnow()
            }
        
        logger.info(f"Remote browser session created: {session_id}")
        
    except Exception as e:
        logger.error(f"Failed to create remote browser session: {e}")
        result = {
            "client_id": client_id,
            "session_id": session_id,
            "status": "failed",
            "error": str(e),
            "message": f"Failed to create remote browser session: {e}"
        }
    
    return result

@tool(
    name="navigate_remote_browser",
    description="Navigate to URL in remote browser session",
    parameters={
        "client_id": {
            "type": "str",
            "description": "Client identifier",
            "required": True
        },
        "session_id": {
            "type": "str",
            "description": "Browser session identifier",
            "required": True
        },
        "url": {
            "type": "str",
            "description": "URL to navigate to",
            "required": True
        },
        "wait_for_load": {
            "type": "bool",
            "description": "Wait for page to load completely",
            "default": True
        }
    }
)
async def navigate_remote_browser(
    client_id: str,
    session_id: str,
    url: str,
    wait_for_load: bool = True
) -> Dict[str, Any]:
    """
    Navigate to URL in remote browser session
    
    This sends a navigation command to the browser extension on the specified client.
    """
    
    logger.info(f"Navigating remote browser: {session_id} to {url}")
    
    command = {
        "type": "NAVIGATE_TO_URL",
        "data": {
            "session_id": session_id,
            "url": url,
            "wait_for_load": wait_for_load
        }
    }
    
    try:
        response = await extension_bridge.send_command_to_client(client_id, command)
        
        result = {
            "client_id": client_id,
            "session_id": session_id,
            "action": "navigate",
            "url": url,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Successfully navigated remote browser to {url}",
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Failed to navigate remote browser: {e}")
        result = {
            "client_id": client_id,
            "session_id": session_id,
            "action": "navigate",
            "url": url,
            "status": "failed",
            "error": str(e),
            "message": f"Failed to navigate remote browser: {e}"
        }
    
    return result

@tool(
    name="click_remote_element",
    description="Click element in remote browser session",
    parameters={
        "client_id": {
            "type": "str",
            "description": "Client identifier",
            "required": True
        },
        "session_id": {
            "type": "str",
            "description": "Browser session identifier",
            "required": True
        },
        "selector": {
            "type": "str",
            "description": "CSS selector of element to click",
            "required": True
        },
        "wait_for_element": {
            "type": "bool",
            "description": "Wait for element to be visible",
            "default": True
        }
    }
)
async def click_remote_element(
    client_id: str,
    session_id: str,
    selector: str,
    wait_for_element: bool = True
) -> Dict[str, Any]:
    """
    Click element in remote browser session
    
    This sends a click command to the browser extension on the specified client.
    """
    
    logger.info(f"Clicking remote element: {selector}")
    
    command = {
        "type": "CLICK_ELEMENT",
        "data": {
            "session_id": session_id,
            "selector": selector,
            "wait_for_element": wait_for_element
        }
    }
    
    try:
        response = await extension_bridge.send_command_to_client(client_id, command)
        
        result = {
            "client_id": client_id,
            "session_id": session_id,
            "action": "click",
            "selector": selector,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Successfully clicked remote element: {selector}",
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Failed to click remote element: {e}")
        result = {
            "client_id": client_id,
            "session_id": session_id,
            "action": "click",
            "selector": selector,
            "status": "failed",
            "error": str(e),
            "message": f"Failed to click remote element: {e}"
        }
    
    return result

@tool(
    name="fill_remote_form_field",
    description="Fill form field in remote browser session",
    parameters={
        "client_id": {
            "type": "str",
            "description": "Client identifier",
            "required": True
        },
        "session_id": {
            "type": "str",
            "description": "Browser session identifier",
            "required": True
        },
        "selector": {
            "type": "str",
            "description": "CSS selector of form field",
            "required": True
        },
        "value": {
            "type": "str",
            "description": "Text to enter in the field",
            "required": True
        },
        "clear_first": {
            "type": "bool",
            "description": "Clear field before entering text",
            "default": True
        }
    }
)
async def fill_remote_form_field(
    client_id: str,
    session_id: str,
    selector: str,
    value: str,
    clear_first: bool = True
) -> Dict[str, Any]:
    """
    Fill form field in remote browser session
    
    This sends a fill command to the browser extension on the specified client.
    """
    
    logger.info(f"Filling remote form field: {selector} with '{value}'")
    
    command = {
        "type": "FILL_FORM_FIELD",
        "data": {
            "session_id": session_id,
            "selector": selector,
            "value": value,
            "clear_first": clear_first
        }
    }
    
    try:
        response = await extension_bridge.send_command_to_client(client_id, command)
        
        result = {
            "client_id": client_id,
            "session_id": session_id,
            "action": "fill",
            "selector": selector,
            "value": value,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Successfully filled remote form field: {selector}",
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Failed to fill remote form field: {e}")
        result = {
            "client_id": client_id,
            "session_id": session_id,
            "action": "fill",
            "selector": selector,
            "value": value,
            "status": "failed",
            "error": str(e),
            "message": f"Failed to fill remote form field: {e}"
        }
    
    return result

@tool(
    name="take_remote_screenshot",
    description="Take screenshot in remote browser session",
    parameters={
        "client_id": {
            "type": "str",
            "description": "Client identifier",
            "required": True
        },
        "session_id": {
            "type": "str",
            "description": "Browser session identifier",
            "required": True
        },
        "full_page": {
            "type": "bool",
            "description": "Take full page screenshot",
            "default": False
        },
        "path": {
            "type": "str",
            "description": "Custom path for screenshot",
            "default": ""
        }
    }
)
async def take_remote_screenshot(
    client_id: str,
    session_id: str,
    full_page: bool = False,
    path: str = ""
) -> Dict[str, Any]:
    """
    Take screenshot in remote browser session
    
    This sends a screenshot command to the browser extension on the specified client.
    """
    
    logger.info(f"Taking remote screenshot: {session_id}")
    
    command = {
        "type": "TAKE_SCREENSHOT",
        "data": {
            "session_id": session_id,
            "full_page": full_page,
            "path": path
        }
    }
    
    try:
        response = await extension_bridge.send_command_to_client(client_id, command)
        
        result = {
            "client_id": client_id,
            "session_id": session_id,
            "action": "screenshot",
            "full_page": full_page,
            "path": path,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Successfully took remote screenshot",
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Failed to take remote screenshot: {e}")
        result = {
            "client_id": client_id,
            "session_id": session_id,
            "action": "screenshot",
            "status": "failed",
            "error": str(e),
            "message": f"Failed to take remote screenshot: {e}"
        }
    
    return result

@tool(
    name="close_remote_browser_session",
    description="Close remote browser session",
    parameters={
        "client_id": {
            "type": "str",
            "description": "Client identifier",
            "required": True
        },
        "session_id": {
            "type": "str",
            "description": "Browser session identifier",
            "required": True
        }
    }
)
async def close_remote_browser_session(
    client_id: str,
    session_id: str
) -> Dict[str, Any]:
    """
    Close remote browser session
    
    This sends a close command to the browser extension on the specified client.
    """
    
    logger.info(f"Closing remote browser session: {session_id}")
    
    command = {
        "type": "CLOSE_BROWSER_SESSION",
        "data": {
            "session_id": session_id
        }
    }
    
    try:
        response = await extension_bridge.send_command_to_client(client_id, command)
        
        # Remove session from tracking
        if client_id in extension_bridge.client_sessions:
            if session_id in extension_bridge.client_sessions[client_id]["active_sessions"]:
                del extension_bridge.client_sessions[client_id]["active_sessions"][session_id]
        
        result = {
            "client_id": client_id,
            "session_id": session_id,
            "action": "close",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Successfully closed remote browser session: {session_id}",
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Failed to close remote browser session: {e}")
        result = {
            "client_id": client_id,
            "session_id": session_id,
            "action": "close",
            "status": "failed",
            "error": str(e),
            "message": f"Failed to close remote browser session: {e}"
        }
    
    return result 