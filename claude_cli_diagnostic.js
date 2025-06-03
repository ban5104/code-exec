const puppeteer = require('puppeteer');

async function diagnoseCLIEnvironment() {
    console.log('Diagnosing Claude Code CLI environment for drag & drop issues...\n');
    
    const browser = await puppeteer.launch({ 
        headless: false,
        devtools: true,
        args: [
            '--no-sandbox', 
            '--disable-setuid-sandbox',
            '--disable-features=VizDisplayCompositor',
            '--allow-file-access-from-files',
            '--disable-web-security'
        ]
    });
    
    const page = await browser.newPage();
    
    // Create a diagnostic page that tests all aspects of file handling
    const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Claude CLI Drag & Drop Diagnostics</title>
        <style>
            body {
                font-family: 'Monaco', 'Consolas', monospace;
                background: #1a1a1a;
                color: #e0e0e0;
                margin: 0;
                padding: 20px;
                font-size: 14px;
            }
            .section {
                background: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }
            .test-area {
                min-height: 100px;
                border: 2px dashed #666;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                background: #333;
                margin: 10px 0;
                transition: all 0.3s ease;
            }
            .test-area.active {
                border-color: #4CAF50;
                background: #2d4a2d;
            }
            .test-area.error {
                border-color: #f44336;
                background: #4a2d2d;
            }
            .log {
                background: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 10px;
                margin: 10px 0;
                max-height: 200px;
                overflow-y: auto;
                font-family: monospace;
                font-size: 12px;
            }
            .log div {
                margin: 2px 0;
                padding: 2px 5px;
            }
            .success { color: #4CAF50; }
            .error { color: #f44336; }
            .warning { color: #FF9800; }
            .info { color: #2196F3; }
            button {
                background: #0066cc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                margin: 5px;
            }
            button:hover { background: #0052a3; }
            .hidden { display: none; }
        </style>
    </head>
    <body>
        <h1>🔍 Claude CLI Drag & Drop Diagnostics</h1>
        
        <div class="section">
            <h3>Environment Detection</h3>
            <div id="envInfo" class="log"></div>
        </div>
        
        <div class="section">
            <h3>Drag & Drop Test Area</h3>
            <div class="test-area" id="dropZone">
                📁 Drop images here or click to select
                <input type="file" id="fileInput" class="hidden" multiple accept="image/*">
            </div>
            <button onclick="document.getElementById('fileInput').click()">Select Files</button>
            <button onclick="testProgrammaticDrop()">Test Programmatic Drop</button>
            <button onclick="clearLogs()">Clear Logs</button>
        </div>
        
        <div class="section">
            <h3>Event Logs</h3>
            <div id="eventLog" class="log"></div>
        </div>
        
        <div class="section">
            <h3>Clipboard Test</h3>
            <div class="test-area" id="pasteArea" tabindex="0">
                📋 Focus here and paste (Ctrl+V)
            </div>
            <div id="clipboardLog" class="log"></div>
        </div>

        <script>
            const dropZone = document.getElementById('dropZone');
            const eventLog = document.getElementById('eventLog');
            const clipboardLog = document.getElementById('clipboardLog');
            const pasteArea = document.getElementById('pasteArea');
            const fileInput = document.getElementById('fileInput');
            const envInfo = document.getElementById('envInfo');
            
            function log(message, type = 'info', target = eventLog) {
                const time = new Date().toLocaleTimeString();
                const div = document.createElement('div');
                div.className = type;
                div.textContent = '[' + time + '] ' + message;
                target.appendChild(div);
                target.scrollTop = target.scrollHeight;
                console.log(message);
            }
            
            function clearLogs() {
                eventLog.innerHTML = '';
                clipboardLog.innerHTML = '';
            }
            
            // Environment detection
            function detectEnvironment() {
                log('User Agent: ' + navigator.userAgent, 'info', envInfo);
                log('Platform: ' + navigator.platform, 'info', envInfo);
                log('Language: ' + navigator.language, 'info', envInfo);
                log('Online: ' + navigator.onLine, 'info', envInfo);
                log('Cookie Enabled: ' + navigator.cookieEnabled, 'info', envInfo);
                log('Secure Context: ' + window.isSecureContext, 'info', envInfo);
                log('Protocol: ' + location.protocol, 'info', envInfo);
                log('Host: ' + location.host, 'info', envInfo);
                
                // API availability
                log('File API: ' + (window.File ? '✓' : '✗'), window.File ? 'success' : 'error', envInfo);
                log('FileReader API: ' + (window.FileReader ? '✓' : '✗'), window.FileReader ? 'success' : 'error', envInfo);
                log('DataTransfer API: ' + (window.DataTransfer ? '✓' : '✗'), window.DataTransfer ? 'success' : 'error', envInfo);
                log('Clipboard API: ' + (navigator.clipboard ? '✓' : '✗'), navigator.clipboard ? 'success' : 'error', envInfo);
                log('Permissions API: ' + (navigator.permissions ? '✓' : '✗'), navigator.permissions ? 'success' : 'error', envInfo);
                
                // Check permissions
                if (navigator.permissions) {
                    navigator.permissions.query({name: 'clipboard-read'}).then(result => {
                        log('Clipboard read permission: ' + result.state, result.state === 'granted' ? 'success' : 'warning', envInfo);
                    }).catch(e => {
                        log('Clipboard permission check failed: ' + e.message, 'error', envInfo);
                    });
                }
                
                // Test DataTransfer creation
                try {
                    const dt = new DataTransfer();
                    log('DataTransfer creation: ✓', 'success', envInfo);
                } catch (e) {
                    log('DataTransfer creation failed: ' + e.message, 'error', envInfo);
                }
                
                // Test File creation
                try {
                    const file = new File(['test'], 'test.txt', {type: 'text/plain'});
                    log('File creation: ✓ (' + file.name + ')', 'success', envInfo);
                } catch (e) {
                    log('File creation failed: ' + e.message, 'error', envInfo);
                }
            }
            
            // Drag and drop handlers
            const dragEvents = ['dragenter', 'dragover', 'dragleave', 'drop'];
            
            dragEvents.forEach(eventType => {
                dropZone.addEventListener(eventType, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    log('Event: ' + eventType, 'info');
                    
                    if (e.dataTransfer) {
                        log('  Types: [' + Array.from(e.dataTransfer.types).join(', ') + ']', 'info');
                        log('  Effect: ' + e.dataTransfer.effectAllowed, 'info');
                        log('  Drop effect: ' + e.dataTransfer.dropEffect, 'info');
                    }
                    
                    if (eventType === 'dragenter') {
                        dropZone.classList.add('active');
                    } else if (eventType === 'dragleave') {
                        dropZone.classList.remove('active');
                    } else if (eventType === 'drop') {
                        dropZone.classList.remove('active');
                        handleFiles(e.dataTransfer.files, 'drag and drop');
                    }
                });
            });
            
            // File input handler
            fileInput.addEventListener('change', (e) => {
                handleFiles(e.target.files, 'file input');
            });
            
            // File handling function
            function handleFiles(files, source) {
                log('Files received from ' + source + ': ' + files.length, files.length > 0 ? 'success' : 'warning');
                
                for (let i = 0; i < files.length; i++) {
                    const file = files[i];
                    log('  File ' + (i+1) + ': ' + file.name, 'success');
                    log('    Type: ' + file.type, 'info');
                    log('    Size: ' + file.size + ' bytes', 'info');
                    log('    Modified: ' + new Date(file.lastModified).toLocaleString(), 'info');
                    
                    // Try to read the file
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = () => {
                            log('    ✓ Image loaded successfully', 'success');
                        };
                        reader.onerror = () => {
                            log('    ✗ Failed to load image', 'error');
                        };
                        reader.readAsDataURL(file);
                    }
                }
            }
            
            // Clipboard handling
            pasteArea.addEventListener('paste', (e) => {
                e.preventDefault();
                log('Paste event detected', 'success', clipboardLog);
                
                const items = e.clipboardData.items;
                log('Clipboard items: ' + items.length, 'info', clipboardLog);
                
                for (let i = 0; i < items.length; i++) {
                    const item = items[i];
                    log('  Item ' + (i+1) + ': kind=' + item.kind + ', type=' + item.type, 'info', clipboardLog);
                    
                    if (item.kind === 'file') {
                        const file = item.getAsFile();
                        if (file) {
                            log('    File: ' + file.name + ' (' + file.type + ', ' + file.size + ' bytes)', 'success', clipboardLog);
                        }
                    } else if (item.kind === 'string') {
                        item.getAsString((str) => {
                            log('    String: ' + str.substring(0, 100) + (str.length > 100 ? '...' : ''), 'info', clipboardLog);
                        });
                    }
                }
            });
            
            // Focus the paste area to enable paste events
            pasteArea.addEventListener('click', () => {
                pasteArea.focus();
                log('Paste area focused', 'info', clipboardLog);
            });
            
            // Programmatic test
            function testProgrammaticDrop() {
                log('Testing programmatic drop...', 'info');
                
                try {
                    const dt = new DataTransfer();
                    const file = new File(['fake image data'], 'test-image.png', {type: 'image/png'});
                    dt.items.add(file);
                    
                    const dropEvent = new DragEvent('drop', {
                        dataTransfer: dt,
                        bubbles: true,
                        cancelable: true
                    });
                    
                    dropZone.dispatchEvent(dropEvent);
                    log('Programmatic drop event dispatched', 'success');
                } catch (e) {
                    log('Programmatic drop failed: ' + e.message, 'error');
                }
            }
            
            // Initialize
            detectEnvironment();
            log('Diagnostic page loaded. Try dragging files!', 'success');
        </script>
    </body>
    </html>
    `;
    
    await page.setContent(htmlContent);
    
    // Take screenshot
    await page.screenshot({ path: 'claude_cli_diagnostic.png', fullPage: true });
    
    console.log('\n📊 Diagnostic page loaded!');
    console.log('🔍 This will help identify why drag & drop might not work in Claude CLI');
    console.log('📋 Try dragging images, using file picker, and pasting');
    console.log('⏰ Browser will stay open for 45 seconds for testing\n');
    
    // Wait for testing
    await new Promise(resolve => setTimeout(resolve, 45000));
    
    // Get final logs
    const finalLogs = await page.evaluate(() => {
        const logs = [];
        document.querySelectorAll('#eventLog div, #clipboardLog div').forEach(div => {
            logs.push(div.textContent);
        });
        return logs;
    });
    
    console.log('\n📝 Test Results Summary:');
    console.log('========================');
    finalLogs.forEach(log => console.log(log));
    
    await browser.close();
}

diagnoseCLIEnvironment().catch(console.error);