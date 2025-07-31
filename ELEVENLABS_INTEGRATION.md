# 🎤 ElevenLabs + MCP Playwright Integration

This guide shows you how to integrate MCP Playwright browser automation with ElevenLabs conversational AI for voice-controlled browser automation.

## 🎯 **Integration Architecture**

```
User Voice → ElevenLabs AI → MCP Server → Browser Extension → Client Browser
```

## 🚀 **Setup Options**

### **Option 1: Browser Extension (Recommended)**

**No client-side dependencies required!**

1. **Install Browser Extension** on any machine
2. **ElevenLabs calls MCP API** 
3. **Browser launches on client machine** automatically

### **Option 2: ElevenLabs Custom Tools**

Create custom tools in ElevenLabs that call your MCP server:

```python
# elevenlabs_tools.py
from elevenlabs import generate, play
import requests

def browser_automation_tool(action, params):
    """ElevenLabs tool for browser automation"""
    mcp_server = "https://playwrightmcp-dzgjhpfxb9e3bbg9.uksouth-01.azurewebsites.net"
    
    response = requests.post(
        f"{mcp_server}/api/v1/tools/{action}/execute",
        json=params,
        headers={"Content-Type": "application/json"}
    )
    
    return response.json()

# Example usage in ElevenLabs
def handle_voice_command(command):
    if "open browser" in command.lower():
        return browser_automation_tool("create_remote_browser_session", {
            "client_id": "user-laptop",
            "session_id": "voice-session",
            "browser": "chrome",
            "headless": False
        })
    elif "go to azure" in command.lower():
        return browser_automation_tool("navigate_remote_browser", {
            "client_id": "user-laptop",
            "session_id": "voice-session",
            "url": "https://portal.azure.com"
        })
```

## 🔧 **Browser Extension Setup**

### **Step 1: Install Extension**

1. **Download the extension files** from `browser-extension/` folder
2. **Open Chrome** and go to `chrome://extensions/`
3. **Enable Developer mode**
4. **Load unpacked** and select the extension folder
5. **Extension is now active** on any machine

### **Step 2: Register Client**

```bash
# Register this machine as a client
curl -X POST "https://playwrightmcp-dzgjhpfxb9e3bbg9.uksouth-01.azurewebsites.net/api/v1/tools/register_browser_extension_client/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "my-laptop",
    "client_info": {
      "browser": "chrome",
      "capabilities": ["browser_automation", "screenshots"],
      "location": "office-desk"
    }
  }'
```

### **Step 3: Voice Commands**

Now you can use voice commands like:

- **"Open a new browser window"**
- **"Navigate to Azure portal"**
- **"Click the login button"**
- **"Fill in my email address"**
- **"Take a screenshot"**

## 🎤 **ElevenLabs Integration Examples**

### **Voice-Controlled Azure Portal**

```python
# elevenlabs_azure_automation.py
import requests
from elevenlabs import generate, play

class VoiceBrowserController:
    def __init__(self, mcp_server_url, client_id):
        self.mcp_server = mcp_server_url
        self.client_id = client_id
        self.session_id = "voice-session"
    
    def execute_browser_action(self, action, params):
        """Execute browser action via MCP server"""
        response = requests.post(
            f"{self.mcp_server}/api/v1/tools/{action}/execute",
            json=params,
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    
    def handle_voice_command(self, voice_text):
        """Handle voice commands and execute browser actions"""
        voice_text = voice_text.lower()
        
        # Browser session management
        if "open browser" in voice_text or "start browser" in voice_text:
            result = self.execute_browser_action("create_remote_browser_session", {
                "client_id": self.client_id,
                "session_id": self.session_id,
                "browser": "chrome",
                "headless": False
            })
            return f"Browser opened successfully. {result.get('message', '')}"
        
        elif "close browser" in voice_text:
            result = self.execute_browser_action("close_remote_browser_session", {
                "client_id": self.client_id,
                "session_id": self.session_id
            })
            return f"Browser closed. {result.get('message', '')}"
        
        # Navigation commands
        elif "go to azure" in voice_text or "open azure" in voice_text:
            result = self.execute_browser_action("navigate_remote_browser", {
                "client_id": self.client_id,
                "session_id": self.session_id,
                "url": "https://portal.azure.com"
            })
            return f"Navigating to Azure portal. {result.get('message', '')}"
        
        elif "go to google" in voice_text:
            result = self.execute_browser_action("navigate_remote_browser", {
                "client_id": self.client_id,
                "session_id": self.session_id,
                "url": "https://google.com"
            })
            return f"Navigating to Google. {result.get('message', '')}"
        
        # Interaction commands
        elif "click" in voice_text and "button" in voice_text:
            # Extract button name from voice command
            button_name = voice_text.split("click")[-1].split("button")[0].strip()
            selector = f"button[contains(text(), '{button_name}')]"
            
            result = self.execute_browser_action("click_remote_element", {
                "client_id": self.client_id,
                "session_id": self.session_id,
                "selector": selector,
                "wait_for_element": True
            })
            return f"Clicked {button_name} button. {result.get('message', '')}"
        
        elif "fill" in voice_text and "email" in voice_text:
            result = self.execute_browser_action("fill_remote_form_field", {
                "client_id": self.client_id,
                "session_id": self.session_id,
                "selector": "input[type='email']",
                "value": "your-email@domain.com",
                "clear_first": True
            })
            return f"Filled email field. {result.get('message', '')}"
        
        elif "take screenshot" in voice_text:
            result = self.execute_browser_action("take_remote_screenshot", {
                "client_id": self.client_id,
                "session_id": self.session_id,
                "full_page": True,
                "path": f"screenshot_voice_{int(time.time())}.png"
            })
            return f"Screenshot taken. {result.get('message', '')}"
        
        else:
            return "I didn't understand that command. Try saying 'open browser' or 'go to Azure'."

# Usage with ElevenLabs
def main():
    controller = VoiceBrowserController(
        mcp_server_url="https://playwrightmcp-dzgjhpfxb9e3bbg9.uksouth-01.azurewebsites.net",
        client_id="my-laptop"
    )
    
    # ElevenLabs voice input
    voice_input = "Open browser and go to Azure portal"
    
    # Process voice command
    response = controller.handle_voice_command(voice_input)
    
    # ElevenLabs voice output
    audio = generate(
        text=response,
        voice="Josh",
        model="eleven_monolingual_v1"
    )
    
    play(audio)

if __name__ == "__main__":
    main()
```

## 🎯 **Voice Command Examples**

### **Basic Browser Control**
- **"Open a new browser window"** → Creates browser session
- **"Close the browser"** → Closes browser session
- **"Take a screenshot"** → Captures current page

### **Navigation**
- **"Go to Azure portal"** → Navigates to portal.azure.com
- **"Open Google"** → Navigates to google.com
- **"Go to my email"** → Navigates to email service

### **Form Interaction**
- **"Fill in my email address"** → Fills email field
- **"Enter my password"** → Fills password field
- **"Click the login button"** → Clicks login button
- **"Submit the form"** → Submits current form

### **Advanced Commands**
- **"Scroll down"** → Scrolls page down
- **"Go back"** → Navigates back
- **"Refresh the page"** → Reloads current page
- **"Open in new tab"** → Opens URL in new tab

## 🔌 **ElevenLabs Webhook Integration**

```python
# elevenlabs_webhook.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/webhook/voice-command', methods=['POST'])
def handle_voice_command():
    """Handle voice commands from ElevenLabs"""
    data = request.json
    voice_text = data.get('text', '')
    
    # Process voice command
    controller = VoiceBrowserController(
        mcp_server_url="https://playwrightmcp-dzgjhpfxb9e3bbg9.uksouth-01.azurewebsites.net",
        client_id=data.get('client_id', 'default')
    )
    
    response = controller.handle_voice_command(voice_text)
    
    return jsonify({
        'success': True,
        'response': response,
        'command': voice_text
    })

if __name__ == '__main__':
    app.run(port=5000)
```

## 🎤 **Real-World Use Cases**

### **1. Voice-Controlled Azure Management**
```bash
# Voice: "Open Azure and show me my virtual machines"
# Action: Opens browser → Navigates to Azure → Goes to VM section
```

### **2. Automated Testing with Voice**
```bash
# Voice: "Run the login test"
# Action: Opens browser → Goes to app → Fills credentials → Clicks login → Takes screenshot
```

### **3. Presentation Mode**
```bash
# Voice: "Start presentation mode"
# Action: Opens browser → Goes to slides → Fullscreen → Starts presentation
```

## 🚀 **Benefits of This Integration**

- ✅ **No client-side dependencies** - Just browser extension
- ✅ **Works on any machine** - Extension handles browser automation
- ✅ **Voice-controlled** - Natural language commands
- ✅ **Real-time feedback** - Voice responses
- ✅ **Cross-platform** - Works on Windows, Mac, Linux
- ✅ **Scalable** - Multiple clients can be registered

## 📋 **Next Steps**

1. **Install the browser extension** on your machine
2. **Register your machine** as a client
3. **Integrate with ElevenLabs** using the provided code
4. **Start using voice commands** for browser automation!

The browser will now launch on **any machine** where the extension is installed when you make voice commands through ElevenLabs! 🎉 