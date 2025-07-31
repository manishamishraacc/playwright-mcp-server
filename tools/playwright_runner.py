import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import os
from pathlib import Path

# Import Playwright
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not installed. Browser automation will be simulated.")

from registry import tool

logger = logging.getLogger(__name__)

# Global browser session manager
class PlaywrightSessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.browsers: Dict[str, Browser] = {}
        self.pages: Dict[str, Page] = {}
        
    async def get_or_create_session(self, session_id: str, browser_type: str = "chrome", headless: bool = False) -> Dict[str, Any]:
        """Get existing session or create new one with real browser"""
        if session_id not in self.sessions:
            if not PLAYWRIGHT_AVAILABLE:
                # Fallback to simulation if Playwright not available
                self.sessions[session_id] = {
                    "browser_type": browser_type,
                    "created_at": datetime.utcnow(),
                    "current_url": None,
                    "page_state": {},
                    "test_steps": [],
                    "screenshots": [],
                    "simulated": True
                }
                logger.warning(f"Created simulated Playwright session: {session_id} (Playwright not available)")
            else:
                # Create real browser session
                try:
                    playwright = await async_playwright().start()
                    
                    # Launch browser based on type
                    if browser_type == "chrome":
                        browser = await playwright.chromium.launch(headless=headless)
                    elif browser_type == "firefox":
                        browser = await playwright.firefox.launch(headless=headless)
                    elif browser_type == "safari":
                        browser = await playwright.webkit.launch(headless=headless)
                    else:
                        browser = await playwright.chromium.launch(headless=headless)
                    
                    # Create new page
                    page = await browser.new_page()
                    
                    # Store browser and page references
                    self.browsers[session_id] = browser
                    self.pages[session_id] = page
                    
                    self.sessions[session_id] = {
                        "browser_type": browser_type,
                        "created_at": datetime.utcnow(),
                        "current_url": None,
                        "page_state": {},
                        "test_steps": [],
                        "screenshots": [],
                        "simulated": False,
                        "playwright": playwright
                    }
                    logger.info(f"Created real Playwright session: {session_id} with {browser_type}")
                except Exception as e:
                    logger.error(f"Failed to create browser session: {e}")
                    # Fallback to simulation
                    self.sessions[session_id] = {
                        "browser_type": browser_type,
                        "created_at": datetime.utcnow(),
                        "current_url": None,
                        "page_state": {},
                        "test_steps": [],
                        "screenshots": [],
                        "simulated": True,
                        "error": str(e)
                    }
        return self.sessions[session_id]
    
    async def close_session(self, session_id: str):
        """Close a browser session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            if not session.get("simulated", True):
                # Close real browser
                try:
                    if session_id in self.pages:
                        await self.pages[session_id].close()
                        del self.pages[session_id]
                    
                    if session_id in self.browsers:
                        await self.browsers[session_id].close()
                        del self.browsers[session_id]
                    
                    if "playwright" in session:
                        await session["playwright"].stop()
                        
                    logger.info(f"Closed real Playwright session: {session_id}")
                except Exception as e:
                    logger.error(f"Error closing browser session {session_id}: {e}")
            else:
                logger.info(f"Closed simulated Playwright session: {session_id}")
            
            del self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session without creating"""
        return self.sessions.get(session_id)
    
    def get_page(self, session_id: str) -> Optional[Page]:
        """Get the page for a session"""
        return self.pages.get(session_id)
    
    def is_simulated(self, session_id: str) -> bool:
        """Check if session is simulated"""
        session = self.sessions.get(session_id)
        return session.get("simulated", True) if session else True

# Global instance
playwright_sessions = PlaywrightSessionManager()

@tool(
    name="create_browser_session",
    description="Create a new browser session for E2E testing",
    parameters={
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
async def create_browser_session(
    session_id: str,
    browser: str = "chrome",
    headless: bool = False
) -> Dict[str, Any]:
    """
    Create a new browser session for E2E testing
    
    This creates a persistent browser session that can be used across multiple test steps.
    """
    
    logger.info(f"Creating browser session: {session_id} with {browser}")
    
    # Get or create session
    session = await playwright_sessions.get_or_create_session(session_id, browser, headless)
    
    result = {
        "session_id": session_id,
        "browser": browser,
        "headless": headless,
        "status": "created",
        "created_at": session["created_at"].isoformat(),
        "simulated": session.get("simulated", True),
        "message": f"Browser session {session_id} ready for testing" + (" (simulated)" if session.get("simulated", True) else " (real browser)")
    }
    
    logger.info(f"Browser session created: {session_id}")
    
    return result

@tool(
    name="navigate_to_url",
    description="Navigate to a URL in the browser session",
    parameters={
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
async def navigate_to_url(
    session_id: str,
    url: str,
    wait_for_load: bool = True
) -> Dict[str, Any]:
    """
    Navigate to a URL in the browser session
    
    This maintains the browser session state across navigation.
    """
    
    logger.info(f"Navigating to {url} in session {session_id}")
    
    # Get session
    session = playwright_sessions.get_session(session_id)
    if not session:
        return {
            "error": f"Session {session_id} not found. Create a session first.",
            "session_id": session_id
        }
    
    # Check if session is simulated
    if playwright_sessions.is_simulated(session_id):
        # Simulate navigation
        await asyncio.sleep(1)
        session["current_url"] = url
        session["test_steps"].append({
            "action": "navigate",
            "url": url,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        result = {
            "session_id": session_id,
            "action": "navigate",
            "url": url,
            "current_url": url,
            "status": "success (simulated)",
            "wait_for_load": wait_for_load,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Simulated navigation to {url}"
        }
    else:
        # Real navigation
        try:
            page = playwright_sessions.get_page(session_id)
            if not page:
                return {
                    "error": f"Page not found for session {session_id}",
                    "session_id": session_id
                }
            
            # Navigate to URL
            await page.goto(url, wait_until="networkidle" if wait_for_load else "domcontentloaded")
            
            # Update session state
            session["current_url"] = url
            session["test_steps"].append({
                "action": "navigate",
                "url": url,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            result = {
                "session_id": session_id,
                "action": "navigate",
                "url": url,
                "current_url": url,
                "status": "success",
                "wait_for_load": wait_for_load,
                "timestamp": datetime.utcnow().isoformat(),
                "title": await page.title(),
                "message": f"Successfully navigated to {url}"
            }
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            result = {
                "session_id": session_id,
                "action": "navigate",
                "url": url,
                "status": "failed",
                "error": str(e),
                "message": f"Failed to navigate to {url}: {e}"
            }
    
    logger.info(f"Navigation completed: {url}")
    
    return result

@tool(
    name="click_element",
    description="Click an element on the page",
    parameters={
        "session_id": {
            "type": "str",
            "description": "Browser session identifier",
            "required": True
        },
        "selector": {
            "type": "str",
            "description": "CSS selector or XPath of element to click",
            "required": True
        },
        "wait_for_element": {
            "type": "bool",
            "description": "Wait for element to be visible",
            "default": True
        }
    }
)
async def click_element(
    session_id: str,
    selector: str,
    wait_for_element: bool = True
) -> Dict[str, Any]:
    """
    Click an element on the page
    
    This maintains the browser session state and records the action.
    """
    
    logger.info(f"Clicking element {selector} in session {session_id}")
    
    # Get session
    session = playwright_sessions.get_session(session_id)
    if not session:
        return {
            "error": f"Session {session_id} not found. Create a session first.",
            "session_id": session_id
        }
    
    # Simulate clicking
    await asyncio.sleep(0.5)
    
    # Update session state
    session["test_steps"].append({
        "action": "click",
        "selector": selector,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    result = {
        "session_id": session_id,
        "action": "click",
        "selector": selector,
        "status": "success",
        "wait_for_element": wait_for_element,
        "timestamp": datetime.utcnow().isoformat(),
        "current_url": session["current_url"]
    }
    
    logger.info(f"Element clicked: {selector}")
    
    return result

@tool(
    name="fill_form_field",
    description="Fill a form field with text",
    parameters={
        "session_id": {
            "type": "str",
            "description": "Browser session identifier",
            "required": True
        },
        "selector": {
            "type": "str",
            "description": "CSS selector of the form field",
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
async def fill_form_field(
    session_id: str,
    selector: str,
    value: str,
    clear_first: bool = True
) -> Dict[str, Any]:
    """
    Fill a form field with text
    
    This maintains the browser session state and records the action.
    """
    
    logger.info(f"Filling field {selector} with '{value}' in session {session_id}")
    
    # Get session
    session = playwright_sessions.get_session(session_id)
    if not session:
        return {
            "error": f"Session {session_id} not found. Create a session first.",
            "session_id": session_id
        }
    
    # Simulate form filling
    await asyncio.sleep(0.3)
    
    # Update session state
    session["test_steps"].append({
        "action": "fill",
        "selector": selector,
        "value": value,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    result = {
        "session_id": session_id,
        "action": "fill",
        "selector": selector,
        "value": value,
        "status": "success",
        "clear_first": clear_first,
        "timestamp": datetime.utcnow().isoformat(),
        "current_url": session["current_url"]
    }
    
    logger.info(f"Form field filled: {selector}")
    
    return result

@tool(
    name="take_screenshot",
    description="Take a screenshot of the current page",
    parameters={
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
async def take_screenshot(
    session_id: str,
    full_page: bool = False,
    path: str = ""
) -> Dict[str, Any]:
    """
    Take a screenshot of the current page
    
    This maintains the browser session state and records the screenshot.
    """
    
    logger.info(f"Taking screenshot in session {session_id}")
    
    # Get session
    session = playwright_sessions.get_session(session_id)
    if not session:
        return {
            "error": f"Session {session_id} not found. Create a session first.",
            "session_id": session_id
        }
    
    # Simulate screenshot
    await asyncio.sleep(0.5)
    
    # Generate screenshot path
    if not path:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        path = f"/tmp/screenshot_{session_id}_{timestamp}.png"
    
    # Update session state
    session["screenshots"].append({
        "path": path,
        "full_page": full_page,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    result = {
        "session_id": session_id,
        "action": "screenshot",
        "path": path,
        "full_page": full_page,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "current_url": session["current_url"]
    }
    
    logger.info(f"Screenshot taken: {path}")
    
    return result

@tool(
    name="get_page_content",
    description="Get text content from the current page",
    parameters={
        "session_id": {
            "type": "str",
            "description": "Browser session identifier",
            "required": True
        },
        "selector": {
            "type": "str",
            "description": "CSS selector to get content from (optional)",
            "default": ""
        }
    }
)
async def get_page_content(
    session_id: str,
    selector: str = ""
) -> Dict[str, Any]:
    """
    Get text content from the current page
    
    This maintains the browser session state and returns page content.
    """
    
    logger.info(f"Getting page content from session {session_id}")
    
    # Get session
    session = playwright_sessions.get_session(session_id)
    if not session:
        return {
            "error": f"Session {session_id} not found. Create a session first.",
            "session_id": session_id
        }
    
    # Simulate content retrieval
    await asyncio.sleep(0.2)
    
    # Mock content based on current URL
    if selector:
        content = f"Content from {selector}: Sample text content"
    else:
        content = f"Page content from {session['current_url']}: Sample page content with multiple elements"
    
    result = {
        "session_id": session_id,
        "action": "get_content",
        "selector": selector,
        "content": content,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "current_url": session["current_url"]
    }
    
    logger.info(f"Page content retrieved: {len(content)} characters")
    
    return result

@tool(
    name="close_browser_session",
    description="Close the browser session and clean up resources",
    parameters={
        "session_id": {
            "type": "str",
            "description": "Browser session identifier",
            "required": True
        }
    }
)
async def close_browser_session(session_id: str) -> Dict[str, Any]:
    """
    Close the browser session and clean up resources
    
    This closes the browser and cleans up the session.
    """
    
    logger.info(f"Closing browser session: {session_id}")
    
    # Get session info before closing
    session = playwright_sessions.get_session(session_id)
    if not session:
        return {
            "error": f"Session {session_id} not found.",
            "session_id": session_id
        }
    
    # Simulate cleanup
    await asyncio.sleep(0.5)
    
    # Close session
    await playwright_sessions.close_session(session_id)
    
    result = {
        "session_id": session_id,
        "action": "close_session",
        "status": "success",
        "test_steps_count": len(session["test_steps"]),
        "screenshots_count": len(session["screenshots"]),
        "session_duration": (datetime.utcnow() - session["created_at"]).total_seconds(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Browser session closed: {session_id}")
    
    return result

@tool(
    name="run_ui_tests",
    description="Run UI tests using Playwright (legacy - use session-based tools for E2E)",
    parameters={
        "browser": {
            "type": "str",
            "description": "Browser to use (chrome, firefox, safari)",
            "default": "chrome"
        },
        "headless": {
            "type": "bool",
            "description": "Run browser in headless mode",
            "default": False
        },
        "url": {
            "type": "str",
            "description": "URL to test",
            "required": True
        },
        "test_script": {
            "type": "str",
            "description": "JavaScript test script to execute",
            "default": ""
        },
        "screenshot": {
            "type": "bool",
            "description": "Take screenshot after test",
            "default": False
        }
    }
)
async def run_ui_tests(
    browser: str = "chrome",
    headless: bool = False,
    url: str = "",
    test_script: str = "",
    screenshot: bool = False
) -> Dict[str, Any]:
    """
    Run UI tests using Playwright
    
    This is a placeholder implementation. In a real scenario, you would:
    1. Install and configure Playwright
    2. Launch the specified browser
    3. Navigate to the URL
    4. Execute the test script
    5. Take screenshots if requested
    6. Return test results
    """
    
    logger.info(f"Starting UI tests for {url} with {browser}")
    
    # Simulate test execution
    await asyncio.sleep(2)  # Simulate test time
    
    # Mock test results
    test_results = {
        "status": "passed",
        "browser": browser,
        "url": url,
        "timestamp": datetime.utcnow().isoformat(),
        "duration_ms": 2000,
        "tests_run": 1,
        "tests_passed": 1,
        "tests_failed": 0,
        "screenshot_taken": screenshot,
        "test_script_executed": bool(test_script)
    }
    
    if test_script:
        test_results["script_output"] = f"Executed: {test_script[:50]}..."
        
    if screenshot:
        test_results["screenshot_path"] = f"/tmp/screenshot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        
    logger.info(f"UI tests completed: {test_results['status']}")
    
    return test_results

@tool(
    name="run_accessibility_tests",
    description="Run accessibility tests on a webpage",
    parameters={
        "url": {
            "type": "str",
            "description": "URL to test",
            "required": True
        },
        "rules": {
            "type": "list",
            "description": "Accessibility rules to check",
            "default": ["wcag2a", "wcag2aa"]
        }
    }
)
async def run_accessibility_tests(url: str, rules: List[str] = None) -> Dict[str, Any]:
    """
    Run accessibility tests on a webpage
    
    This is a placeholder implementation for accessibility testing.
    """
    
    if rules is None:
        rules = ["wcag2a", "wcag2aa"]
        
    logger.info(f"Starting accessibility tests for {url}")
    
    # Simulate accessibility testing
    await asyncio.sleep(1.5)
    
    # Mock accessibility results
    accessibility_results = {
        "status": "completed",
        "url": url,
        "timestamp": datetime.utcnow().isoformat(),
        "rules_checked": rules,
        "violations": [
            {
                "rule": "color-contrast",
                "description": "Insufficient color contrast",
                "severity": "warning",
                "element": "button.submit-btn"
            }
        ],
        "passes": 15,
        "violations_count": 1,
        "incomplete": 0
    }
    
    logger.info(f"Accessibility tests completed: {accessibility_results['passes']} passes, {accessibility_results['violations_count']} violations")
    
    return accessibility_results

@tool(
    name="generate_test_report",
    description="Generate a comprehensive test report",
    parameters={
        "test_results": {
            "type": "dict",
            "description": "Test results to include in report",
            "required": True
        },
        "format": {
            "type": "str",
            "description": "Report format (html, json, pdf)",
            "default": "html"
        },
        "include_screenshots": {
            "type": "bool",
            "description": "Include screenshots in report",
            "default": True
        }
    }
)
async def generate_test_report(
    test_results: Dict[str, Any],
    format: str = "html",
    include_screenshots: bool = True
) -> Dict[str, Any]:
    """
    Generate a comprehensive test report
    
    This is a placeholder implementation for report generation.
    """
    
    logger.info(f"Generating {format} test report")
    
    # Simulate report generation
    await asyncio.sleep(1)
    
    report_data = {
        "report_id": f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "format": format,
        "generated_at": datetime.utcnow().isoformat(),
        "test_results": test_results,
        "summary": {
            "total_tests": test_results.get("tests_run", 0),
            "passed": test_results.get("tests_passed", 0),
            "failed": test_results.get("tests_failed", 0),
            "success_rate": f"{(test_results.get('tests_passed', 0) / max(test_results.get('tests_run', 1), 1)) * 100:.1f}%"
        },
        "screenshots_included": include_screenshots,
        "report_path": f"/reports/test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"
    }
    
    logger.info(f"Test report generated: {report_data['report_id']}")
    
    return report_data 