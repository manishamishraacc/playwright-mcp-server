// Content script for MCP Browser Controller
// This script runs in web pages to handle browser automation commands

console.log('MCP Browser Controller content script loaded');

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Content script received message:', message);
    
    switch (message.type) {
        case 'CLICK_ELEMENT':
            handleClickElement(message, sendResponse);
            return true;
            
        case 'FILL_FORM_FIELD':
            handleFillFormField(message, sendResponse);
            return true;
            
        case 'GET_PAGE_CONTENT':
            handleGetPageContent(message, sendResponse);
            return true;
            
        default:
            sendResponse({ error: 'Unknown message type in content script' });
    }
});

async function handleClickElement(message, sendResponse) {
    try {
        const { selector, wait_for_element } = message;
        
        let element = null;
        
        if (wait_for_element) {
            // Wait for element to be present
            element = await waitForElement(selector);
        } else {
            // Try to find element immediately
            element = document.querySelector(selector);
        }
        
        if (!element) {
            throw new Error(`Element not found: ${selector}`);
        }
        
        // Scroll element into view
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Wait a bit for scroll to complete
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Click the element
        element.click();
        
        console.log(`Clicked element: ${selector}`);
        
        sendResponse({
            status: 'success',
            selector: selector,
            message: `Successfully clicked ${selector}`
        });
        
    } catch (error) {
        console.error('Error clicking element:', error);
        sendResponse({ error: error.message });
    }
}

async function handleFillFormField(message, sendResponse) {
    try {
        const { selector, value, clear_first } = message;
        
        let element = await waitForElement(selector);
        
        if (!element) {
            throw new Error(`Form field not found: ${selector}`);
        }
        
        // Scroll element into view
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Wait a bit for scroll to complete
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Focus the element
        element.focus();
        
        if (clear_first) {
            // Clear existing value
            element.value = '';
            // Trigger input event
            element.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        // Set the new value
        element.value = value;
        
        // Trigger input and change events
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        
        console.log(`Filled form field: ${selector} with "${value}"`);
        
        sendResponse({
            status: 'success',
            selector: selector,
            value: value,
            message: `Successfully filled ${selector}`
        });
        
    } catch (error) {
        console.error('Error filling form field:', error);
        sendResponse({ error: error.message });
    }
}

async function handleGetPageContent(message, sendResponse) {
    try {
        const { selector } = message;
        
        let content = '';
        let title = document.title;
        
        if (selector) {
            // Get content from specific selector
            const element = document.querySelector(selector);
            if (element) {
                content = element.textContent || element.innerText || '';
            } else {
                throw new Error(`Element not found: ${selector}`);
            }
        } else {
            // Get full page content
            content = document.body.textContent || document.body.innerText || '';
        }
        
        console.log(`Got page content: ${content.substring(0, 100)}...`);
        
        sendResponse({
            status: 'success',
            selector: selector,
            content: content,
            title: title,
            message: `Successfully got content from ${selector || 'page'}`
        });
        
    } catch (error) {
        console.error('Error getting page content:', error);
        sendResponse({ error: error.message });
    }
}

// Utility function to wait for an element to be present
function waitForElement(selector, timeout = 10000) {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        
        const checkElement = () => {
            const element = document.querySelector(selector);
            
            if (element) {
                resolve(element);
                return;
            }
            
            if (Date.now() - startTime > timeout) {
                reject(new Error(`Element not found within ${timeout}ms: ${selector}`));
                return;
            }
            
            // Check again in 100ms
            setTimeout(checkElement, 100);
        };
        
        checkElement();
    });
}

// Inject custom styles for better visibility
const style = document.createElement('style');
style.textContent = `
    .mcp-highlight {
        outline: 3px solid #ff6b6b !important;
        outline-offset: 2px !important;
        background-color: rgba(255, 107, 107, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .mcp-clicked {
        outline: 3px solid #4ecdc4 !important;
        background-color: rgba(78, 205, 196, 0.2) !important;
    }
`;
document.head.appendChild(style);

// Add visual feedback for interactions
function highlightElement(selector, className = 'mcp-highlight') {
    const element = document.querySelector(selector);
    if (element) {
        element.classList.add(className);
        setTimeout(() => {
            element.classList.remove(className);
        }, 2000);
    }
}

// Listen for page load events
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded, MCP Browser Controller ready');
});

// Listen for navigation events
window.addEventListener('load', () => {
    console.log('Page fully loaded, MCP Browser Controller active');
}); 