const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function testDragAndDrop() {
    const browser = await puppeteer.launch({ 
        headless: false, // Keep visible to see what happens
        devtools: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // Create a simple HTML page that mimics a CLI-like interface
    const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                background: #1e1e1e;
                color: #d4d4d4;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .cli-container {
                background: #000;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 20px;
                min-height: 400px;
                position: relative;
            }
            .drop-zone {
                border: 2px dashed #555;
                border-radius: 8px;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                background: #2d2d30;
                transition: all 0.3s ease;
            }
            .drop-zone.drag-over {
                border-color: #007acc;
                background: #0e293d;
            }
            .prompt {
                color: #569cd6;
            }
            .log {
                margin: 10px 0;
                padding: 5px;
                background: #2d2d30;
                border-radius: 4px;
                font-size: 12px;
            }
            .error { color: #f48771; }
            .success { color: #4ec9b0; }
            .info { color: #9cdcfe; }
        </style>
    </head>
    <body>
        <div class="cli-container">
            <div class="prompt">claude-code@terminal:~$</div>
            <p>Testing drag and drop functionality...</p>
            
            <div class="drop-zone" id="dropZone">
                <p>📁 Drop images here</p>
                <p style="font-size: 12px; opacity: 0.7;">Supported: PNG, JPG, GIF, WebP</p>
            </div>
            
            <div id="logs"></div>
        </div>

        <script>
            const dropZone = document.getElementById('dropZone');
            const logs = document.getElementById('logs');
            
            function addLog(message, type = 'info') {
                const log = document.createElement('div');
                log.className = 'log ' + type;
                log.textContent = new Date().toLocaleTimeString() + ': ' + message;
                logs.appendChild(log);
                console.log(message);
            }
            
            // Drag and drop event listeners
            dropZone.addEventListener('dragenter', (e) => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
                addLog('Drag enter detected', 'info');
            });
            
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                addLog('Drag over detected', 'info');
            });
            
            dropZone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                addLog('Drag leave detected', 'info');
            });
            
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                
                const files = Array.from(e.dataTransfer.files);
                addLog('Drop detected! Files: ' + files.length, 'success');
                
                files.forEach((file, index) => {
                    addLog('File ' + (index + 1) + ': ' + file.name + ' (' + file.type + ', ' + file.size + ' bytes)', 'success');
                    
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            addLog('Image loaded successfully: ' + file.name, 'success');
                            // Could display preview here
                        };
                        reader.onerror = () => {
                            addLog('Error reading file: ' + file.name, 'error');
                        };
                        reader.readAsDataURL(file);
                    }
                });
            });
            
            // Additional event listeners for debugging
            document.addEventListener('dragstart', (e) => {
                addLog('Document dragstart: ' + e.target.tagName, 'info');
            });
            
            document.addEventListener('dragend', (e) => {
                addLog('Document dragend', 'info');
            });
            
            // Test programmatic drag and drop
            window.testDragDrop = function() {
                addLog('Testing programmatic drag and drop...', 'info');
                
                // Create a fake file
                const dt = new DataTransfer();
                const file = new File(['test content'], 'test-image.png', { type: 'image/png' });
                dt.items.add(file);
                
                // Create and dispatch drop event
                const dropEvent = new DragEvent('drop', {
                    dataTransfer: dt,
                    bubbles: true,
                    cancelable: true
                });
                
                dropZone.dispatchEvent(dropEvent);
            };
            
            addLog('Drag and drop test page loaded', 'success');
        </script>
    </body>
    </html>
    `;
    
    await page.setContent(htmlContent);
    
    // Take initial screenshot
    await page.screenshot({ path: 'drag_drop_initial.png', fullPage: true });
    
    // Test programmatic drag and drop
    await page.evaluate(() => {
        window.testDragDrop();
    });
    
    // Wait a bit for events to process
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Take screenshot after test
    await page.screenshot({ path: 'drag_drop_after_test.png', fullPage: true });
    
    // Get console logs
    const logs = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('.log')).map(log => log.textContent);
    });
    
    console.log('Test logs:');
    logs.forEach(log => console.log(log));
    
    // Keep browser open for manual testing
    console.log('\nBrowser is open for manual testing. Try dragging and dropping images!');
    console.log('Press Ctrl+C to close when done.');
    
    // Wait for user to manually test or interrupt
    await new Promise(resolve => setTimeout(resolve, 30000)); // Wait 30 seconds
    
    await browser.close();
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\nClosing browser...');
    process.exit(0);
});

testDragAndDrop().catch(console.error);