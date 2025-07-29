import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Global instances
from registry import ToolRegistry
from context.memory import SessionManager

tool_registry = ToolRegistry()
session_manager = SessionManager()

# Import and register tools
import tools.playwright_runner
import tools.azure_devops

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def register_tools():
    """Register all available tools"""
    # Register session-based Playwright tools for E2E testing
    tool_registry.register_tool(
        tools.playwright_runner.create_browser_session,
        name="create_browser_session",
        description="Create a new browser session for E2E testing",
        parameters=tools.playwright_runner.create_browser_session._tool_parameters
    )
    
    tool_registry.register_tool(
        tools.playwright_runner.navigate_to_url,
        name="navigate_to_url",
        description="Navigate to a URL in the browser session",
        parameters=tools.playwright_runner.navigate_to_url._tool_parameters
    )
    
    tool_registry.register_tool(
        tools.playwright_runner.click_element,
        name="click_element",
        description="Click an element on the page",
        parameters=tools.playwright_runner.click_element._tool_parameters
    )
    
    tool_registry.register_tool(
        tools.playwright_runner.fill_form_field,
        name="fill_form_field",
        description="Fill a form field with text",
        parameters=tools.playwright_runner.fill_form_field._tool_parameters
    )
    
    tool_registry.register_tool(
        tools.playwright_runner.take_screenshot,
        name="take_screenshot",
        description="Take a screenshot of the current page",
        parameters=tools.playwright_runner.take_screenshot._tool_parameters
    )
    
    tool_registry.register_tool(
        tools.playwright_runner.get_page_content,
        name="get_page_content",
        description="Get text content from the current page",
        parameters=tools.playwright_runner.get_page_content._tool_parameters
    )
    
    tool_registry.register_tool(
        tools.playwright_runner.close_browser_session,
        name="close_browser_session",
        description="Close the browser session and clean up resources",
        parameters=tools.playwright_runner.close_browser_session._tool_parameters
    )
    
    # Register legacy Playwright tools
    tool_registry.register_tool(
        tools.playwright_runner.run_ui_tests,
        name="run_ui_tests",
        description="Run UI tests using Playwright (legacy - use session-based tools for E2E)",
        parameters=tools.playwright_runner.run_ui_tests._tool_parameters
    )
    
    tool_registry.register_tool(
        tools.playwright_runner.run_accessibility_tests,
        name="run_accessibility_tests",
        description="Run accessibility tests on a webpage",
        parameters=tools.playwright_runner.run_accessibility_tests._tool_parameters
    )
    
    tool_registry.register_tool(
        tools.playwright_runner.generate_test_report,
        name="generate_test_report",
        description="Generate a comprehensive test report",
        parameters=tools.playwright_runner.generate_test_report._tool_parameters
    )
    
    # Register tools from azure_devops
    tool_registry.register_tool(
        tools.azure_devops.get_release_info,
        name="get_release_info",
        description="Get release information from Azure DevOps",
        parameters=tools.azure_devops.get_release_info._tool_parameters
    )
    
    tool_registry.register_tool(
        tools.azure_devops.create_release,
        name="create_release",
        description="Create a new release in Azure DevOps",
        parameters=tools.azure_devops.create_release._tool_parameters
    )
    
    tool_registry.register_tool(
        tools.azure_devops.get_build_info,
        name="get_build_info",
        description="Get build information from Azure DevOps",
        parameters=tools.azure_devops.get_build_info._tool_parameters
    )
    
    tool_registry.register_tool(
        tools.azure_devops.trigger_build,
        name="trigger_build",
        description="Trigger a new build in Azure DevOps",
        parameters=tools.azure_devops.trigger_build._tool_parameters
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting MCP Server...")
    
    # Initialize session manager
    await session_manager.initialize()
    logger.info("Session manager initialized")
    
    # Initialize tool registry
    await tool_registry.initialize()
    logger.info("Tool registry initialized")
    
    # Register tools
    await register_tools()
    logger.info("Tools registered")
    
    yield
    
    logger.info("Shutting down MCP Server...")
    # Cleanup sessions
    await session_manager.cleanup()

app = FastAPI(
    title="MCP Server",
    description="Model Context Protocol Server with FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include MCP routes
from routes.mcp import router as mcp_router
app.include_router(mcp_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "MCP Server is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "tools_registered": len(tool_registry.tools),
        "active_sessions": len(session_manager.sessions)
    }

@app.get("/test")
async def test():
    """Test endpoint"""
    return {
        "message": "Test endpoint working",
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_fixed:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    ) 