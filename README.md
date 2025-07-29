# Playwright MCP Server

A FastAPI-based Model Context Protocol (MCP) server that provides AI-powered test automation capabilities using Playwright and Azure DevOps integration.

## 🚀 Features

- **AI-Powered Test Automation**: Leverage AI to create and execute browser automation tests
- **Playwright Integration**: Full browser automation with Chrome, Firefox, and Safari support
- **Azure DevOps Integration**: Manage releases, builds, and deployments
- **Session-Based Testing**: Maintain browser sessions for complex E2E testing workflows
- **Real-time Communication**: WebSocket support for live interaction
- **Comprehensive API**: RESTful API with automatic documentation

## 🛠️ Available Tools

### Playwright Tools (Session-based E2E Testing)
- `create_browser_session` - Create a new browser session
- `navigate_to_url` - Navigate to a URL
- `click_element` - Click an element on the page
- `fill_form_field` - Fill a form field with text
- `take_screenshot` - Take a screenshot
- `get_page_content` - Get text content from the page
- `close_browser_session` - Close the browser session

### Legacy Playwright Tools
- `run_ui_tests` - Run UI tests using Playwright
- `run_accessibility_tests` - Run accessibility tests
- `generate_test_report` - Generate test reports

### Azure DevOps Tools
- `get_release_info` - Get release information
- `create_release` - Create a new release
- `get_build_info` - Get build information
- `trigger_build` - Trigger a new build

## 📋 Prerequisites

- Python 3.9+
- Playwright
- FastAPI
- Uvicorn

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd playwright-mcp-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   playwright install
   ```

## 🏃‍♂️ Quick Start

1. **Start the server**
   ```bash
   python main_fixed.py
   ```

2. **Access the API documentation**
   - Swagger UI: http://localhost:8002/docs
   - ReDoc: http://localhost:8002/redoc

3. **Test the API**
   ```bash
   # Get all available tools
   curl http://localhost:8002/api/v1/tools
   
   # Health check
   curl http://localhost:8002/health
   ```

## 📚 API Endpoints

### Core Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /test` - Test endpoint

### MCP Endpoints (with `/api/v1` prefix)
- `GET /api/v1/tools` - List all available tools
- `GET /api/v1/tools/{tool_name}` - Get specific tool information
- `POST /api/v1/tools/{tool_name}/execute` - Execute a tool directly
- `POST /api/v1/chat` - Process chat requests
- `POST /api/v1/chat/stream` - Stream chat responses
- `GET /api/v1/sessions` - List all active sessions
- `GET /api/v1/sessions/{session_id}` - Get session information
- `DELETE /api/v1/sessions/{session_id}` - Delete a session
- `WS /api/v1/ws/{session_id}` - WebSocket endpoint for real-time communication

## 🔧 Configuration

The server runs on port 8002 by default. You can modify the configuration in `main_fixed.py`:

```python
uvicorn.run(
    "main_fixed:app",
    host="0.0.0.0",
    port=8002,
    reload=True,
    log_level="info"
)
```

## 🧪 Usage Examples

### Creating a Browser Session
```bash
curl -X POST "http://localhost:8002/api/v1/tools/create_browser_session/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-1",
    "browser": "chrome",
    "headless": false
  }'
```

### Navigating to a URL
```bash
curl -X POST "http://localhost:8002/api/v1/tools/navigate_to_url/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-1",
    "url": "https://example.com",
    "wait_for_load": true
  }'
```

### Taking a Screenshot
```bash
curl -X POST "http://localhost:8002/api/v1/tools/take_screenshot/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-1",
    "full_page": true,
    "path": "screenshot.png"
  }'
```

## 🏗️ Project Structure

```
playwright-mcp-server/
├── agents/                 # AI agent implementations
│   ├── __init__.py
│   └── base_agent.py
├── context/               # Session and memory management
│   ├── __init__.py
│   └── memory.py
├── routes/                # API route definitions
│   ├── __init__.py
│   └── mcp.py
├── schemas/               # Pydantic models and schemas
│   ├── __init__.py
│   └── mcp.py
├── tools/                 # Tool implementations
│   ├── __init__.py
│   ├── playwright_runner.py
│   └── azure_devops.py
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── helpers.py
├── main_fixed.py          # Main application entry point
├── main.py                # Alternative main file
├── registry.py            # Tool registry
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔍 Development

### Running in Development Mode
The server includes auto-reload functionality for development:

```bash
python main_fixed.py
```

### Adding New Tools
1. Create your tool function in the appropriate module under `tools/`
2. Register it in the `register_tools()` function in `main_fixed.py`
3. The tool will be automatically available via the API

### Testing
```bash
# Run the test script
python test_tools_api.py

# Or use the example client
python example_client.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [API documentation](http://localhost:8002/docs) when the server is running
2. Review the logs for error messages
3. Open an issue on GitHub with detailed information about the problem

## 🔗 Related Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Playwright Documentation](https://playwright.dev/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Azure DevOps REST API](https://docs.microsoft.com/en-us/rest/api/azure/devops/) 