# 🎯 Browser Extension Setup Guide

This guide will help you install and use the MCP Browser Controller extension for client-side browser automation.

## 📋 **Prerequisites**

- **Google Chrome** browser (version 88 or later)
- **Internet connection** to connect to MCP server
- **MCP server** running at `https://playwrightmcp-dzgjhpfxb9e3bbg9.uksouth-01.azurewebsites.net`

## 🚀 **Step-by-Step Installation**

### **Step 1: Download Extension Files**

1. **Create a folder** on your computer (e.g., `mcp-browser-extension`)
2. **Copy all files** from the `browser-extension/` folder to your new folder:
   - `manifest.json`
   - `background.js`
   - `content-script.js`
   - `popup.html`
   - `popup.js`

### **Step 2: Load Extension in Chrome**

1. **Open Chrome** and go to `chrome://extensions/`
2. **Enable Developer mode** (toggle in top-right corner)
3. **Click "Load unpacked"** button
4. **Select your extension folder** (the folder you created in Step 1)
5. **Extension should appear** in the extensions list

### **Step 3: Verify Installation**

1. **Look for the extension icon** in Chrome toolbar (🎯 icon)
2. **Click the icon** to open the popup
3. **You should see** the MCP Browser Controller interface

## 🔧 **First-Time Setup**

### **Step 1: Register Your Machine**

1. **Click the extension icon** in Chrome toolbar
2. **Click "📝 Register This Machine"** button
3. **Wait for registration** to complete
4. **You should see** "✅ Registered" status

### **Step 2: Test Connection**

1. **Check the status indicator** (green dot = connected, red dot = disconnected)
2. **Status should show** "Connected to MCP Server"
3. **If disconnected**, check your internet connection

## 🎯 **Using the Extension**

### **Manual Control (Popup Interface)**

1. **Click extension icon** to open popup
2. **Use the buttons** to control browser automation:
   - **🖥️ Create Browser Session** - Opens a new browser tab
   - **🌐 Navigate to Azure** - Goes to Azure portal
   - **📸 Take Screenshot** - Captures current page
   - **🔒 Close Session** - Closes browser tab

### **Voice Control (ElevenLabs Integration)**

Once registered, you can use voice commands through ElevenLabs:

```bash
# Voice: "Open a new browser window"
# Action: Creates browser session

# Voice: "Navigate to Azure portal"  
# Action: Goes to portal.azure.com

# Voice: "Take a screenshot"
# Action: Captures and saves screenshot
```

## 🔍 **Troubleshooting**

### **Extension Not Loading**

**Problem:** Extension doesn't appear in Chrome
**Solution:**
1. Check that all files are in the folder
2. Verify `manifest.json` is valid JSON
3. Try refreshing the extensions page
4. Check Chrome console for errors

### **Registration Fails**

**Problem:** "Registration failed" error
**Solution:**
1. Check internet connection
2. Verify MCP server is running
3. Check browser console for detailed error
4. Try refreshing and retrying

### **Connection Issues**

**Problem:** Red status indicator (disconnected)
**Solution:**
1. Check internet connection
2. Verify MCP server URL is correct
3. Check if server is running
4. Try refreshing the popup

### **Browser Session Not Opening**

**Problem:** Clicking "Create Browser Session" does nothing
**Solution:**
1. Make sure you're registered first
2. Check browser console for errors
3. Verify popup blocker isn't blocking
4. Try refreshing the extension

## 📊 **Extension Features**

### **✅ What It Does**

- **Creates browser sessions** on your machine
- **Navigates to URLs** automatically
- **Takes screenshots** and saves to Downloads
- **Clicks elements** on web pages
- **Fills form fields** with text
- **Works with voice commands** via ElevenLabs

### **🔧 Technical Details**

- **Manifest V3** - Latest Chrome extension standard
- **Background Service Worker** - Handles browser automation
- **Content Scripts** - Interacts with web pages
- **Popup Interface** - User-friendly controls
- **Storage API** - Remembers settings and sessions

## 🎤 **Voice Command Examples**

### **Basic Commands**
```bash
"Open browser"           → Creates new browser session
"Go to Azure"           → Navigates to portal.azure.com
"Take screenshot"       → Captures current page
"Close browser"         → Closes browser session
```

### **Advanced Commands**
```bash
"Click the login button"     → Clicks login button
"Fill in my email"          → Fills email field
"Go to Google"              → Navigates to google.com
"Refresh the page"          → Reloads current page
```

## 🔒 **Security & Permissions**

### **Required Permissions**

- **`activeTab`** - Access to current tab
- **`storage`** - Save settings and session data
- **`scripting`** - Execute scripts in tabs
- **`downloads`** - Save screenshots

### **Host Permissions**

- **MCP Server** - Connect to your MCP server
- **Azure Portal** - Navigate to Azure
- **All URLs** - Work with any website

## 🚀 **Advanced Usage**

### **Multiple Machines**

You can install the extension on multiple machines:

1. **Install extension** on each machine
2. **Register each machine** with unique client ID
3. **Control any machine** from your MCP server

### **Custom URLs**

Modify the popup to navigate to custom URLs:

```javascript
// In popup.js, change the URL
url: 'https://your-custom-url.com'
```

### **Batch Operations**

Use the MCP server to send multiple commands:

```bash
# Create session
curl -X POST "..." -d '{"client_id": "your-machine", "session_id": "test"}'

# Navigate
curl -X POST "..." -d '{"client_id": "your-machine", "session_id": "test", "url": "https://example.com"}'

# Take screenshot
curl -X POST "..." -d '{"client_id": "your-machine", "session_id": "test"}'
```

## 📞 **Support**

### **Getting Help**

1. **Check browser console** for error messages
2. **Verify MCP server** is running and accessible
3. **Test with simple commands** first
4. **Check network connectivity**

### **Common Issues**

- **CORS errors** - Check MCP server CORS settings
- **Permission denied** - Check extension permissions
- **Session not found** - Create session first
- **Navigation failed** - Check URL validity

## 🎉 **Success Indicators**

You know it's working when:

- ✅ **Green status indicator** in popup
- ✅ **"Registered" button** shows ✅
- ✅ **Browser tabs open** when you create sessions
- ✅ **Screenshots save** to Downloads folder
- ✅ **Voice commands work** through ElevenLabs

## 🚀 **Next Steps**

1. **Test basic functionality** with popup buttons
2. **Try voice commands** with ElevenLabs
3. **Explore advanced features** like form filling
4. **Set up multiple machines** for distributed automation

The extension is now ready to enable **client-side browser automation** on any machine where it's installed! 🎯 