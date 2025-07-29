import requests
import json

def test_tools_api():
    """Test the tools API endpoint"""
    
    # Test different possible endpoints
    endpoints = [
        "http://localhost:8002/tools",
        "http://localhost:8002/api/v1/tools", 
        "http://localhost:8000/tools",
        "http://localhost:8000/api/v1/tools"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint}")
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_tools_api() 