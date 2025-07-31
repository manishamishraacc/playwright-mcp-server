// Popup script for MCP Browser Controller
const MCP_SERVER_URL = 'https://playwrightmcp-dzgjhpfxb9e3bbg9.uksouth-01.azurewebsites.net';

// DOM elements
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const sessionInfo = document.getElementById('sessionInfo');
const sessionId = document.getElementById('sessionId');
const currentUrl = document.getElementById('currentUrl');

// Buttons
const registerBtn = document.getElementById('registerBtn');
const createSessionBtn = document.getElementById('createSessionBtn');
const navigateBtn = document.getElementById('navigateBtn');
const screenshotBtn = document.getElementById('screenshotBtn');
const closeSessionBtn = document.getElementById('closeSessionBtn');

// State
let isConnected = false;
let clientId = null;
let activeSessionId = null;

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Popup loaded');
    
    // Check connection status
    await checkConnection();
    
    // Load stored data
    await loadStoredData();
    
    // Update UI
    updateUI();
});

// Check connection to MCP server
async function checkConnection() {
    try {
        const response = await fetch(`${MCP_SERVER_URL}/health`);
        if (response.ok) {
            isConnected = true;
            statusIndicator.className = 'status-indicator status-connected';
            statusText.textContent = 'Connected to MCP Server';
        } else {
            throw new Error('Server not responding');
        }
    } catch (error) {
        console.error('Connection check failed:', error);
        isConnected = false;
        statusIndicator.className = 'status-indicator status-disconnected';
        statusText.textContent = 'Disconnected from MCP Server';
    }
}

// Load stored data from extension storage
async function loadStoredData() {
    try {
        const result = await chrome.storage.local.get(['clientId', 'activeSessionId']);
        clientId = result.clientId;
        activeSessionId = result.activeSessionId;
        
        if (activeSessionId) {
            sessionInfo.classList.remove('hidden');
            sessionId.textContent = activeSessionId;
        }
    } catch (error) {
        console.error('Failed to load stored data:', error);
    }
}

// Update UI based on current state
function updateUI() {
    // Enable/disable buttons based on connection
    const buttons = [registerBtn, createSessionBtn, navigateBtn, screenshotBtn, closeSessionBtn];
    buttons.forEach(btn => {
        btn.disabled = !isConnected;
    });
    
    // Show/hide session info
    if (activeSessionId) {
        sessionInfo.classList.remove('hidden');
        sessionId.textContent = activeSessionId;
    } else {
        sessionInfo.classList.add('hidden');
    }
}

// Register this machine as a client
registerBtn.addEventListener('click', async () => {
    try {
        registerBtn.disabled = true;
        registerBtn.textContent = 'Registering...';
        
        // Generate unique client ID
        clientId = `client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        const response = await fetch(`${MCP_SERVER_URL}/api/v1/tools/register_browser_extension_client/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                client_id: clientId,
                client_info: {
                    browser: 'chrome',
                    capabilities: ['browser_automation', 'screenshots', 'form_filling'],
                    extension_version: '1.0.0',
                    user_agent: navigator.userAgent
                }
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Registration successful:', result);
            
            // Store client ID
            await chrome.storage.local.set({ clientId });
            
            // Show success message
            statusText.textContent = `Registered as ${clientId}`;
            registerBtn.textContent = '✅ Registered';
            registerBtn.disabled = true;
            
        } else {
            throw new Error(`Registration failed: ${response.status}`);
        }
        
    } catch (error) {
        console.error('Registration failed:', error);
        statusText.textContent = `Registration failed: ${error.message}`;
        registerBtn.textContent = '❌ Failed - Retry';
        registerBtn.disabled = false;
    }
});

// Create browser session
createSessionBtn.addEventListener('click', async () => {
    try {
        if (!clientId) {
            alert('Please register this machine first!');
            return;
        }
        
        createSessionBtn.disabled = true;
        createSessionBtn.textContent = 'Creating...';
        
        activeSessionId = `session-${Date.now()}`;
        
        const response = await fetch(`${MCP_SERVER_URL}/api/v1/tools/create_remote_browser_session/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                client_id: clientId,
                session_id: activeSessionId,
                browser: 'chrome',
                headless: false
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Session created:', result);
            
            // Store session ID
            await chrome.storage.local.set({ activeSessionId });
            
            // Update UI
            updateUI();
            
            createSessionBtn.textContent = '✅ Session Created';
            statusText.textContent = `Browser session ${activeSessionId} created`;
            
        } else {
            throw new Error(`Session creation failed: ${response.status}`);
        }
        
    } catch (error) {
        console.error('Session creation failed:', error);
        statusText.textContent = `Session creation failed: ${error.message}`;
        createSessionBtn.textContent = '❌ Failed - Retry';
        createSessionBtn.disabled = false;
    }
});

// Navigate to Azure
navigateBtn.addEventListener('click', async () => {
    try {
        if (!activeSessionId) {
            alert('Please create a browser session first!');
            return;
        }
        
        navigateBtn.disabled = true;
        navigateBtn.textContent = 'Navigating...';
        
        const response = await fetch(`${MCP_SERVER_URL}/api/v1/tools/navigate_remote_browser/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                client_id: clientId,
                session_id: activeSessionId,
                url: 'https://portal.azure.com',
                wait_for_load: true
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Navigation successful:', result);
            
            currentUrl.textContent = 'https://portal.azure.com';
            navigateBtn.textContent = '✅ Navigated';
            statusText.textContent = 'Successfully navigated to Azure Portal';
            
        } else {
            throw new Error(`Navigation failed: ${response.status}`);
        }
        
    } catch (error) {
        console.error('Navigation failed:', error);
        statusText.textContent = `Navigation failed: ${error.message}`;
        navigateBtn.textContent = '❌ Failed - Retry';
    } finally {
        navigateBtn.disabled = false;
    }
});

// Take screenshot
screenshotBtn.addEventListener('click', async () => {
    try {
        if (!activeSessionId) {
            alert('Please create a browser session first!');
            return;
        }
        
        screenshotBtn.disabled = true;
        screenshotBtn.textContent = 'Taking Screenshot...';
        
        const response = await fetch(`${MCP_SERVER_URL}/api/v1/tools/take_remote_screenshot/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                client_id: clientId,
                session_id: activeSessionId,
                full_page: true,
                path: `screenshot_${Date.now()}.png`
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Screenshot taken:', result);
            
            screenshotBtn.textContent = '✅ Screenshot Taken';
            statusText.textContent = 'Screenshot saved to Downloads';
            
        } else {
            throw new Error(`Screenshot failed: ${response.status}`);
        }
        
    } catch (error) {
        console.error('Screenshot failed:', error);
        statusText.textContent = `Screenshot failed: ${error.message}`;
        screenshotBtn.textContent = '❌ Failed - Retry';
    } finally {
        screenshotBtn.disabled = false;
    }
});

// Close session
closeSessionBtn.addEventListener('click', async () => {
    try {
        if (!activeSessionId) {
            alert('No active session to close!');
            return;
        }
        
        closeSessionBtn.disabled = true;
        closeSessionBtn.textContent = 'Closing...';
        
        const response = await fetch(`${MCP_SERVER_URL}/api/v1/tools/close_remote_browser_session/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                client_id: clientId,
                session_id: activeSessionId
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Session closed:', result);
            
            // Clear session data
            activeSessionId = null;
            await chrome.storage.local.remove(['activeSessionId']);
            
            // Update UI
            updateUI();
            
            closeSessionBtn.textContent = '✅ Session Closed';
            statusText.textContent = 'Browser session closed successfully';
            
        } else {
            throw new Error(`Session close failed: ${response.status}`);
        }
        
    } catch (error) {
        console.error('Session close failed:', error);
        statusText.textContent = `Session close failed: ${error.message}`;
        closeSessionBtn.textContent = '❌ Failed - Retry';
    } finally {
        closeSessionBtn.disabled = false;
    }
});

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Popup received message:', message);
    
    if (message.type === 'SESSION_UPDATED') {
        activeSessionId = message.sessionId;
        updateUI();
    }
    
    sendResponse({ received: true });
}); 