// Background service worker for MCP Browser Controller
const MCP_SERVER_URL = 'https://playwrightmcp-dzgjhpfxb9e3bbg9.uksouth-01.azurewebsites.net';

// Store active sessions
let activeSessions = new Map();

// Listen for messages from content scripts and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Background received message:', message);
    
    switch (message.type) {
        case 'CREATE_BROWSER_SESSION':
            handleCreateSession(message.data, sendResponse);
            return true; // Keep message channel open for async response
            
        case 'NAVIGATE_TO_URL':
            handleNavigate(message.data, sendResponse);
            return true;
            
        case 'CLICK_ELEMENT':
            handleClick(message.data, sendResponse);
            return true;
            
        case 'FILL_FORM_FIELD':
            handleFillField(message.data, sendResponse);
            return true;
            
        case 'TAKE_SCREENSHOT':
            handleScreenshot(message.data, sendResponse);
            return true;
            
        case 'CLOSE_BROWSER_SESSION':
            handleCloseSession(message.data, sendResponse);
            return true;
            
        case 'GET_PAGE_CONTENT':
            handleGetContent(message.data, sendResponse);
            return true;
            
        default:
            sendResponse({ error: 'Unknown message type' });
    }
});

async function handleCreateSession(data, sendResponse) {
    try {
        const { session_id, browser, headless } = data;
        
        // Create a new tab for the browser session
        const tab = await chrome.tabs.create({
            url: 'about:blank',
            active: !headless
        });
        
        // Store session info
        activeSessions.set(session_id, {
            tabId: tab.id,
            browser: browser,
            headless: headless,
            created_at: new Date().toISOString()
        });
        
        console.log(`Created browser session: ${session_id} in tab ${tab.id}`);
        
        sendResponse({
            session_id: session_id,
            browser: browser,
            headless: headless,
            status: 'created',
            tab_id: tab.id,
            message: 'Browser session created successfully'
        });
        
    } catch (error) {
        console.error('Error creating session:', error);
        sendResponse({ error: error.message });
    }
}

async function handleNavigate(data, sendResponse) {
    try {
        const { session_id, url, wait_for_load } = data;
        const session = activeSessions.get(session_id);
        
        if (!session) {
            throw new Error(`Session ${session_id} not found`);
        }
        
        // Navigate the tab to the URL
        await chrome.tabs.update(session.tabId, { url: url });
        
        // Wait for page load if requested
        if (wait_for_load) {
            await new Promise(resolve => {
                chrome.tabs.onUpdated.addListener(function listener(tabId, changeInfo) {
                    if (tabId === session.tabId && changeInfo.status === 'complete') {
                        chrome.tabs.onUpdated.removeListener(listener);
                        resolve();
                    }
                });
            });
        }
        
        console.log(`Navigated session ${session_id} to ${url}`);
        
        sendResponse({
            session_id: session_id,
            action: 'navigate',
            url: url,
            status: 'success',
            message: `Successfully navigated to ${url}`
        });
        
    } catch (error) {
        console.error('Error navigating:', error);
        sendResponse({ error: error.message });
    }
}

async function handleClick(data, sendResponse) {
    try {
        const { session_id, selector, wait_for_element } = data;
        const session = activeSessions.get(session_id);
        
        if (!session) {
            throw new Error(`Session ${session_id} not found`);
        }
        
        // Send click command to content script
        const response = await chrome.tabs.sendMessage(session.tabId, {
            type: 'CLICK_ELEMENT',
            selector: selector,
            wait_for_element: wait_for_element
        });
        
        sendResponse(response);
        
    } catch (error) {
        console.error('Error clicking element:', error);
        sendResponse({ error: error.message });
    }
}

async function handleFillField(data, sendResponse) {
    try {
        const { session_id, selector, value, clear_first } = data;
        const session = activeSessions.get(session_id);
        
        if (!session) {
            throw new Error(`Session ${session_id} not found`);
        }
        
        // Send fill command to content script
        const response = await chrome.tabs.sendMessage(session.tabId, {
            type: 'FILL_FORM_FIELD',
            selector: selector,
            value: value,
            clear_first: clear_first
        });
        
        sendResponse(response);
        
    } catch (error) {
        console.error('Error filling field:', error);
        sendResponse({ error: error.message });
    }
}

async function handleScreenshot(data, sendResponse) {
    try {
        const { session_id, full_page, path } = data;
        const session = activeSessions.get(session_id);
        
        if (!session) {
            throw new Error(`Session ${session_id} not found`);
        }
        
        // Take screenshot using chrome.tabs.captureVisibleTab
        const screenshot = await chrome.tabs.captureVisibleTab(session.tabId, {
            format: 'png',
            quality: 100
        });
        
        // Convert base64 to blob and download
        const response = await fetch(screenshot);
        const blob = await response.blob();
        
        // Create download link
        const url = URL.createObjectURL(blob);
        const filename = path || `screenshot_${Date.now()}.png`;
        
        await chrome.downloads.download({
            url: url,
            filename: filename,
            saveAs: false
        });
        
        console.log(`Screenshot saved: ${filename}`);
        
        sendResponse({
            session_id: session_id,
            action: 'screenshot',
            path: filename,
            full_page: full_page,
            status: 'success',
            message: `Screenshot saved as ${filename}`
        });
        
    } catch (error) {
        console.error('Error taking screenshot:', error);
        sendResponse({ error: error.message });
    }
}

async function handleCloseSession(data, sendResponse) {
    try {
        const { session_id } = data;
        const session = activeSessions.get(session_id);
        
        if (!session) {
            throw new Error(`Session ${session_id} not found`);
        }
        
        // Close the tab
        await chrome.tabs.remove(session.tabId);
        
        // Remove from active sessions
        activeSessions.delete(session_id);
        
        console.log(`Closed browser session: ${session_id}`);
        
        sendResponse({
            session_id: session_id,
            action: 'close',
            status: 'success',
            message: `Browser session ${session_id} closed`
        });
        
    } catch (error) {
        console.error('Error closing session:', error);
        sendResponse({ error: error.message });
    }
}

async function handleGetContent(data, sendResponse) {
    try {
        const { session_id, selector } = data;
        const session = activeSessions.get(session_id);
        
        if (!session) {
            throw new Error(`Session ${session_id} not found`);
        }
        
        // Send get content command to content script
        const response = await chrome.tabs.sendMessage(session.tabId, {
            type: 'GET_PAGE_CONTENT',
            selector: selector
        });
        
        sendResponse(response);
        
    } catch (error) {
        console.error('Error getting content:', error);
        sendResponse({ error: error.message });
    }
}

// Handle tab removal to clean up sessions
chrome.tabs.onRemoved.addListener((tabId) => {
    // Find and remove session for this tab
    for (const [session_id, session] of activeSessions.entries()) {
        if (session.tabId === tabId) {
            activeSessions.delete(session_id);
            console.log(`Cleaned up session ${session_id} (tab ${tabId} was closed)`);
            break;
        }
    }
});

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
    console.log('MCP Browser Controller extension installed');
}); 