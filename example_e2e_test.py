#!/usr/bin/env python3
"""
Example E2E test using session-based Playwright tools
Demonstrates how to maintain browser state across multiple test steps
"""

import asyncio
import json
import httpx
from typing import Dict, Any

class E2ETestClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/tools/{tool_name}/execute",
                json=arguments
            )
            return response.json()
    
    async def run_login_test(self):
        """Example E2E test: Login flow"""
        print("🚀 Starting E2E Login Test")
        print("=" * 50)
        
        # Step 1: Create browser session
        print("1. Creating browser session...")
        result = await self.execute_tool("create_browser_session", {
            "session_id": "login-test-session",
            "browser": "chrome",
            "headless": True
        })
        print(f"   ✅ Session created: {result.get('session_id')}")
        self.session_id = result.get('session_id')
        
        # Step 2: Navigate to login page
        print("\n2. Navigating to login page...")
        result = await self.execute_tool("navigate_to_url", {
            "session_id": self.session_id,
            "url": "https://example.com/login",
            "wait_for_load": True
        })
        print(f"   ✅ Navigated to: {result.get('current_url')}")
        
        # Step 3: Fill username field
        print("\n3. Filling username field...")
        result = await self.execute_tool("fill_form_field", {
            "session_id": self.session_id,
            "selector": "#username",
            "value": "testuser@example.com",
            "clear_first": True
        })
        print(f"   ✅ Username filled: {result.get('value')}")
        
        # Step 4: Fill password field
        print("\n4. Filling password field...")
        result = await self.execute_tool("fill_form_field", {
            "session_id": self.session_id,
            "selector": "#password",
            "value": "securepassword123",
            "clear_first": True
        })
        print(f"   ✅ Password filled: {result.get('value')}")
        
        # Step 5: Click login button
        print("\n5. Clicking login button...")
        result = await self.execute_tool("click_element", {
            "session_id": self.session_id,
            "selector": "#login-button",
            "wait_for_element": True
        })
        print(f"   ✅ Login button clicked")
        
        # Step 6: Wait and take screenshot
        print("\n6. Taking screenshot after login...")
        await asyncio.sleep(2)  # Wait for page to load
        result = await self.execute_tool("take_screenshot", {
            "session_id": self.session_id,
            "full_page": True,
            "path": "/tmp/login_success.png"
        })
        print(f"   ✅ Screenshot taken: {result.get('path')}")
        
        # Step 7: Verify login success
        print("\n7. Verifying login success...")
        result = await self.execute_tool("get_page_content", {
            "session_id": self.session_id,
            "selector": ".welcome-message"
        })
        print(f"   ✅ Page content: {result.get('content')}")
        
        # Step 8: Close session
        print("\n8. Closing browser session...")
        result = await self.execute_tool("close_browser_session", {
            "session_id": self.session_id
        })
        print(f"   ✅ Session closed. Test steps: {result.get('test_steps_count')}")
        
        print("\n🎉 E2E Login Test Completed Successfully!")
        return True
    
    async def run_shopping_cart_test(self):
        """Example E2E test: Shopping cart flow"""
        print("\n🛒 Starting E2E Shopping Cart Test")
        print("=" * 50)
        
        # Step 1: Create browser session
        print("1. Creating browser session...")
        result = await self.execute_tool("create_browser_session", {
            "session_id": "shopping-cart-test-session",
            "browser": "chrome",
            "headless": True
        })
        print(f"   ✅ Session created: {result.get('session_id')}")
        self.session_id = result.get('session_id')
        
        # Step 2: Navigate to product page
        print("\n2. Navigating to product page...")
        result = await self.execute_tool("navigate_to_url", {
            "session_id": self.session_id,
            "url": "https://example.com/products/laptop",
            "wait_for_load": True
        })
        print(f"   ✅ Navigated to: {result.get('current_url')}")
        
        # Step 3: Add item to cart
        print("\n3. Adding item to cart...")
        result = await self.execute_tool("click_element", {
            "session_id": self.session_id,
            "selector": ".add-to-cart-btn",
            "wait_for_element": True
        })
        print(f"   ✅ Item added to cart")
        
        # Step 4: Navigate to cart
        print("\n4. Navigating to shopping cart...")
        result = await self.execute_tool("navigate_to_url", {
            "session_id": self.session_id,
            "url": "https://example.com/cart",
            "wait_for_load": True
        })
        print(f"   ✅ Navigated to cart: {result.get('current_url')}")
        
        # Step 5: Verify item in cart
        print("\n5. Verifying item in cart...")
        result = await self.execute_tool("get_page_content", {
            "session_id": self.session_id,
            "selector": ".cart-item-name"
        })
        print(f"   ✅ Cart item: {result.get('content')}")
        
        # Step 6: Update quantity
        print("\n6. Updating item quantity...")
        result = await self.execute_tool("fill_form_field", {
            "session_id": self.session_id,
            "selector": ".quantity-input",
            "value": "2",
            "clear_first": True
        })
        print(f"   ✅ Quantity updated: {result.get('value')}")
        
        # Step 7: Take screenshot
        print("\n7. Taking screenshot of cart...")
        result = await self.execute_tool("take_screenshot", {
            "session_id": self.session_id,
            "full_page": False,
            "path": "/tmp/shopping_cart.png"
        })
        print(f"   ✅ Screenshot taken: {result.get('path')}")
        
        # Step 8: Close session
        print("\n8. Closing browser session...")
        result = await self.execute_tool("close_browser_session", {
            "session_id": self.session_id
        })
        print(f"   ✅ Session closed. Test steps: {result.get('test_steps_count')}")
        
        print("\n🎉 E2E Shopping Cart Test Completed Successfully!")
        return True

async def run_all_tests():
    """Run all E2E tests"""
    client = E2ETestClient()
    
    try:
        # Test server connection
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(f"{client.base_url}/health")
            if response.status_code != 200:
                print("❌ Server not available. Start the server first.")
                return False
        
        # Run tests
        await client.run_login_test()
        await client.run_shopping_cart_test()
        
        print("\n" + "=" * 50)
        print("🎉 All E2E tests completed successfully!")
        print("The session-based approach maintains browser state across all test steps.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("E2E Test Demo - Session-based Playwright Tools")
    print("This demonstrates how browser sessions persist across multiple test steps.")
    print("Make sure the MCP server is running: uvicorn main:app --reload")
    print()
    
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1) 