const puppeteer = require('puppeteer');

async function testTerminalDragDrop() {
    console.log('Testing drag and drop in terminal-like environment...');
    
    const browser = await puppeteer.launch({ 
        headless: false,
        args: [
            '--no-sandbox', 
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--allow-file-access-from-files'
        ]
    });
    
    const page = await browser.newPage();
    
    // Simulate a terminal/CLI interface
    const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * { box-sizing: border-box; }
            body {
                font-family: 'Courier New', monospace;
                background: #000;
                color: #00ff00;
                margin: 0;
                padding: 0;
                overflow: hidden;
                height: 100vh;
                width: 100vw;
            }
            .terminal {
                width: 100%;
                height: 100%;
                padding: 10px;
                background: #000;
                border: none;
                outline: none;
                position: relative;
            }
            .content {
                height: 100%;
                width: 100%;
                display: flex;
                flex-direction: column;
            }
            .header {
                color: #ffff00;
                margin-bottom: 10px;
            }
            .input-area {
                flex: 1;
                border: 1px dashed #333;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #111;
                position: relative;
            }
            .status {
                position: absolute;
                top: 10px;
                right: 10px;
                font-size: 12px;
                color: #888;
            }
            .logs {
                height: 200px;
                overflow-y: auto;
                background: #222;
                padding: 10px;
                font-size: 12px;
                border-top: 1px solid #333;
            }
        </style>
    </head>
    <body>
        <div class="terminal">
            <div class="content">
                <div class="header">Claude Code CLI - Drag & Drop Test</div>
                <div class="status" id="status">Ready</div>
                
                <div class="input-area" id="dropArea">
                    <div>Drop files here or paste images...</div>
                </div>
                
                <div class="logs" id="logs"></div>
            </div>
        </div>

        <script>
            const dropArea = document.getElementById('dropArea');
            const logs = document.getElementById('logs');
            const status = document.getElementById('status');
            
            function log(message, type = 'info') {
                const time = new Date().toLocaleTimeString();
                const color = type === 'error' ? '#ff4444' : type === 'success' ? '#44ff44' : '#ffffff';
                logs.innerHTML += '<div style="color:' + color + '">[' + time + '] ' + message + '</div>';
                logs.scrollTop = logs.scrollHeight;
                console.log(message);
            }
            
            // Test all possible drag/drop events
            const events = ['dragenter', 'dragover', 'dragleave', 'drop'];
            
            events.forEach(eventName => {
                dropArea.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    log('Event: ' + eventName + ' - DataTransfer types: ' + Array.from(e.dataTransfer?.types || []).join(', '));
                    
                    if (eventName === 'dragenter') {
                        status.textContent = 'Dragging...';
                        dropArea.style.background = '#003300';
                    } else if (eventName === 'dragleave') {
                        status.textContent = 'Ready';
                        dropArea.style.background = '#111';
                    } else if (eventName === 'drop') {
                        status.textContent = 'Processing...';
                        dropArea.style.background = '#111';
                        
                        const files = e.dataTransfer.files;
                        const items = e.dataTransfer.items;
                        
                        log('Files dropped: ' + files.length, 'success');
                        log('DataTransfer items: ' + items.length, 'success');
                        
                        for (let i = 0; i < files.length; i++) {
                            const file = files[i];
                            log('File ' + (i+1) + ': ' + file.name + ' (type: ' + file.type + ', size: ' + file.size + ')', 'success');
                        }
                        
                        for (let i = 0; i < items.length; i++) {
                            const item = items[i];
                            log('Item ' + (i+1) + ': kind=' + item.kind + ', type=' + item.type, 'success');
                        }
                        
                        status.textContent = 'Ready';
                    }
                });
                
                // Also add to document for debugging
                document.addEventListener(eventName, (e) => {
                    if (e.target !== dropArea) {
                        log('Document ' + eventName + ' (target: ' + e.target.tagName + ')');
                    }
                });
            });
            
            // Test paste events
            document.addEventListener('paste', (e) => {
                e.preventDefault();
                log('Paste event detected', 'success');
                
                const items = e.clipboardData.items;
                log('Clipboard items: ' + items.length, 'success');
                
                for (let i = 0; i < items.length; i++) {
                    const item = items[i];
                    log('Clipboard item ' + (i+1) + ': kind=' + item.kind + ', type=' + item.type, 'success');
                    
                    if (item.kind === 'file') {
                        const file = item.getAsFile();
                        log('Pasted file: ' + file.name + ' (type: ' + file.type + ', size: ' + file.size + ')', 'success');
                    }
                }
            });
            
            // Test security and permissions
            log('Testing environment capabilities...');
            log('User agent: ' + navigator.userAgent);
            log('Platform: ' + navigator.platform);
            log('Clipboard API available: ' + (navigator.clipboard ? 'Yes' : 'No'));
            log('File API available: ' + (window.File ? 'Yes' : 'No'));
            log('DataTransfer API available: ' + (window.DataTransfer ? 'Yes' : 'No'));
            
            // Check if we're in a secure context
            log('Secure context: ' + (window.isSecureContext ? 'Yes' : 'No'));
            
            // Test programmatic file creation
            try {
                const testFile = new File(['test'], 'test.txt', { type: 'text/plain' });
                log('File constructor works: ' + testFile.name, 'success');
            } catch (e) {
                log('File constructor error: ' + e.message, 'error');
            }
            
            log('Setup complete. Try dragging files or pasting images!', 'success');
        </script>
    </body>
    </html>
    `;
    
    await page.setContent(htmlContent);
    
    // Enable clipboard permissions
    await page.evaluate(() => {
        // Simulate focus to enable paste events
        document.body.focus();
    });
    
    // Take initial screenshot
    await page.screenshot({ path: 'terminal_test_initial.png', fullPage: true });
    
    console.log('Terminal test page loaded. Browser window should be open.');
    console.log('Try dragging and dropping images into the browser window.');
    console.log('Also try copying an image and pasting with Ctrl+V');
    console.log('Press Ctrl+C to close when done testing.');
    
    // Wait for manual interaction
    await new Promise(resolve => setTimeout(resolve, 45000));
    
    // Take final screenshot
    await page.screenshot({ path: 'terminal_test_final.png', fullPage: true });
    
    await browser.close();
}

testTerminalDragDrop().catch(console.error);