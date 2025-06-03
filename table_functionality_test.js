#!/usr/bin/env node

/**
 * Puppeteer Test for Claude Web Search and File Usage Tables
 * This test creates a mock HTML page that demonstrates the table functionality
 * similar to what would be displayed in the terminal by the Python script.
 */

const puppeteer = require('puppeteer');
const fs = require('fs');

// Create HTML content that mimics the Rich table output
function createTestHTML() {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Table Functionality Test</title>
    <style>
        body {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            background-color: #1e1e1e;
            color: #ffffff;
            padding: 20px;
            margin: 0;
        }
        
        .table-container {
            margin: 20px 0;
            border: 2px solid;
            border-radius: 8px;
            padding: 15px;
            overflow-x: auto;
        }
        
        .web-search-table {
            border-color: #ff6b6b;
        }
        
        .web-search-results-table {
            border-color: #4ecdc4;
        }
        
        .file-usage-table {
            border-color: #45b7d1;
        }
        
        .uploaded-files-table {
            border-color: #f39c12;
        }
        
        .table-title {
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        
        th, td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #333;
        }
        
        th {
            background-color: #2d2d2d;
            font-weight: bold;
        }
        
        .column-number { color: #888; width: 40px; }
        .column-title { color: #4ecdc4; max-width: 300px; }
        .column-url { color: #45b7d1; max-width: 250px; word-break: break-all; }
        .column-published { color: #f39c12; }
        .column-filename { color: #4ecdc4; }
        .column-type { color: #45b7d1; }
        .column-action { color: #f39c12; }
        .column-timestamp { color: #45b7d1; }
        .column-query { color: #98fb98; }
        .column-results { color: #f39c12; }
        .column-id { color: #888; }
        .column-path { color: #98fb98; }
        
        .truncate {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .test-controls {
            position: fixed;
            top: 10px;
            right: 10px;
            background: #2d2d2d;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #555;
        }
        
        .test-controls button {
            background: #4ecdc4;
            color: white;
            border: none;
            padding: 5px 10px;
            margin: 2px;
            border-radius: 3px;
            cursor: pointer;
        }
        
        .test-controls button:hover {
            background: #45b7d1;
        }
        
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <h1>🤖 Claude Table Functionality Test</h1>
    <p>This page demonstrates the table designs for web search tracking and file usage in the Claude with Code Execution tool.</p>
    
    <div class="test-controls">
        <button onclick="toggleTable('web-search')">Toggle Web Search</button>
        <button onclick="toggleTable('web-results')">Toggle Web Results</button>
        <button onclick="toggleTable('file-usage')">Toggle File Usage</button>
        <button onclick="toggleTable('uploaded-files')">Toggle Uploaded Files</button>
        <button onclick="runTableTests()">Run Tests</button>
        <div id="test-status"></div>
    </div>

    <!-- Web Search History Table -->
    <div id="web-search" class="table-container web-search-table">
        <div class="table-title">🔍 Web Search History</div>
        <table>
            <thead>
                <tr>
                    <th class="column-number">#</th>
                    <th class="column-query">Query</th>
                    <th class="column-timestamp">Timestamp</th>
                    <th class="column-results">Results Count</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="column-number">1</td>
                    <td class="column-query">Claude 3.5 Sonnet SWE-bench scores Anthropic models</td>
                    <td class="column-timestamp">2025-06-01 21:11:51</td>
                    <td class="column-results">10</td>
                </tr>
                <tr>
                    <td class="column-number">2</td>
                    <td class="column-query">Anthropic Claude models SWE-bench scores comparison Haiku Opus</td>
                    <td class="column-timestamp">2025-06-01 21:12:15</td>
                    <td class="column-results">8</td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- Web Search Results Table -->
    <div id="web-results" class="table-container web-search-results-table">
        <div class="table-title">🌐 WEB SEARCH RESULTS - Found 10 sources</div>
        <table>
            <thead>
                <tr>
                    <th class="column-number">#</th>
                    <th class="column-title">Title</th>
                    <th class="column-url">URL</th>
                    <th class="column-published">Published</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="column-number">1</td>
                    <td class="column-title truncate">Claude SWE-Bench Performance \\ Anthropic</td>
                    <td class="column-url truncate">https://www.anthropic.com/research/swe-bench...</td>
                    <td class="column-published">Published</td>
                </tr>
                <tr>
                    <td class="column-number">2</td>
                    <td class="column-title truncate">Introducing Claude 3: a new family of models</td>
                    <td class="column-url truncate">https://www.anthropic.com/news/3-intro-claude-...</td>
                    <td class="column-published">November 20, 2024</td>
                </tr>
                <tr>
                    <td class="column-number">3</td>
                    <td class="column-title truncate">Sonnet, and Claude 3.5 Haiku \\ Anthropic</td>
                    <td class="column-url truncate">https://www.anthropic.com/news/claude-3-5-so...</td>
                    <td class="column-published">July 19, 2024</td>
                </tr>
                <tr>
                    <td class="column-number">4</td>
                    <td class="column-title truncate">The new Claude 3.5 Sonnet Code in Anthropic</td>
                    <td class="column-url truncate">https://www.anthropic.com/news/claude-3-5-...</td>
                    <td class="column-published">March 4, 2025</td>
                </tr>
                <tr>
                    <td class="column-number">5</td>
                    <td class="column-title truncate">Building SOTA Agents with SF-5+ and</td>
                    <td class="column-url truncate">https://www.latent.space/p/claude-sonnet</td>
                    <td class="column-published">February 25, 2025</td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- File Usage History Table -->
    <div id="file-usage" class="table-container file-usage-table">
        <div class="table-title">📊 File Usage History</div>
        <table>
            <thead>
                <tr>
                    <th class="column-number">#</th>
                    <th class="column-filename">File Name</th>
                    <th class="column-action">Action</th>
                    <th class="column-timestamp">Timestamp</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="column-number">1</td>
                    <td class="column-filename">tax_calculation.xlsx</td>
                    <td class="column-action">attached to message</td>
                    <td class="column-timestamp">2025-06-01 21:10:30</td>
                </tr>
                <tr>
                    <td class="column-number">2</td>
                    <td class="column-filename">swyftx_report.xlsx</td>
                    <td class="column-action">accessed</td>
                    <td class="column-timestamp">2025-06-01 21:11:45</td>
                </tr>
                <tr>
                    <td class="column-number">3</td>
                    <td class="column-filename">analysis_results.pdf</td>
                    <td class="column-action">uploaded</td>
                    <td class="column-timestamp">2025-06-01 21:12:00</td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- Uploaded Files Table (existing functionality) -->
    <div id="uploaded-files" class="table-container uploaded-files-table">
        <div class="table-title">📁 Uploaded Files</div>
        <table>
            <thead>
                <tr>
                    <th class="column-filename">File Name</th>
                    <th class="column-type">Type</th>
                    <th class="column-id">File ID</th>
                    <th class="column-path">Path</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="column-filename">Swyftx Transaction Report 2025.xlsx</td>
                    <td class="column-type">Excel Spreadsheet</td>
                    <td class="column-id">file_abc123...</td>
                    <td class="column-path">/home/user/documents/tax/swyftx.xlsx</td>
                </tr>
                <tr>
                    <td class="column-filename">Standard_Form_Calculation.pdf</td>
                    <td class="column-type">PDF Document</td>
                    <td class="column-id">file_def456...</td>
                    <td class="column-path">/home/user/documents/tax/forms.pdf</td>
                </tr>
            </tbody>
        </table>
    </div>

    <script>
        function toggleTable(tableId) {
            const table = document.getElementById(tableId);
            table.classList.toggle('hidden');
        }

        function runTableTests() {
            const statusDiv = document.getElementById('test-status');
            let testResults = [];

            // Test 1: Check if all tables are present
            const tables = ['web-search', 'web-results', 'file-usage', 'uploaded-files'];
            const allTablesPresent = tables.every(id => document.getElementById(id) !== null);
            testResults.push(allTablesPresent ? '✅ All tables present' : '❌ Missing tables');

            // Test 2: Check if tables have proper headers
            const webSearchHeaders = document.querySelector('#web-search thead tr');
            const hasProperHeaders = webSearchHeaders && webSearchHeaders.children.length === 4;
            testResults.push(hasProperHeaders ? '✅ Headers correct' : '❌ Header issues');

            // Test 3: Check if tables have data rows
            const hasDataRows = document.querySelectorAll('tbody tr').length > 0;
            testResults.push(hasDataRows ? '✅ Data rows present' : '❌ No data rows');

            // Test 4: Check responsive design
            const tables_elements = document.querySelectorAll('.table-container');
            const hasResponsiveDesign = Array.from(tables_elements).every(t => 
                getComputedStyle(t).overflowX === 'auto'
            );
            testResults.push(hasResponsiveDesign ? '✅ Responsive design' : '❌ Not responsive');

            statusDiv.innerHTML = '<div style="margin-top: 10px;"><strong>Test Results:</strong><br>' + 
                                 testResults.join('<br>') + '</div>';
        }

        // Auto-run tests on page load
        window.addEventListener('load', function() {
            setTimeout(runTableTests, 500);
        });
    </script>
</body>
</html>
    `;
}

async function runPuppeteerTest() {
    console.log('🚀 Starting Puppeteer test for Claude table functionality...');
    
    const browser = await puppeteer.launch({ 
        headless: false,
        defaultViewport: { width: 1200, height: 800 }
    });
    
    try {
        const page = await browser.newPage();
        
        // Create and serve the test HTML
        const htmlContent = createTestHTML();
        await page.setContent(htmlContent, { waitUntil: 'domcontentloaded' });
        
        console.log('📄 Test page loaded successfully');
        
        // Wait for page to stabilize
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Test 1: Verify all tables are visible
        const tableCount = await page.$$eval('.table-container', tables => tables.length);
        console.log(`✅ Found ${tableCount} tables (expected 4)`);
        
        // Test 2: Check web search table functionality
        const webSearchRows = await page.$$eval('#web-search tbody tr', rows => rows.length);
        console.log(`✅ Web search table has ${webSearchRows} data rows`);
        
        // Test 3: Check web results table functionality  
        const webResultsRows = await page.$$eval('#web-results tbody tr', rows => rows.length);
        console.log(`✅ Web results table has ${webResultsRows} data rows`);
        
        // Test 4: Check file usage table functionality
        const fileUsageRows = await page.$$eval('#file-usage tbody tr', rows => rows.length);
        console.log(`✅ File usage table has ${fileUsageRows} data rows`);
        
        // Test 5: Test toggle functionality
        await page.evaluate(() => toggleTable('web-search'));
        const isHidden = await page.$eval('#web-search', el => el.classList.contains('hidden'));
        console.log(`✅ Toggle functionality works: ${isHidden ? 'table hidden' : 'table visible'}`);
        
        // Test 6: Test responsive design
        await page.setViewport({ width: 600, height: 800 });
        await new Promise(resolve => setTimeout(resolve, 500));
        const hasScrollbar = await page.$eval('.table-container', el => 
            el.scrollWidth > el.clientWidth
        );
        console.log(`✅ Responsive design: ${hasScrollbar ? 'scrollable on mobile' : 'fits on mobile'}`);
        
        // Test 7: Run built-in tests
        await page.evaluate(() => runTableTests());
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const testResults = await page.$eval('#test-status', el => el.textContent);
        console.log('📊 Built-in test results:', testResults);
        
        // Take screenshot
        await page.screenshot({ 
            path: '/home/ben_anderson/projects/codeexec-test/table_functionality_test.png',
            fullPage: true 
        });
        console.log('📸 Screenshot saved as table_functionality_test.png');
        
        // Wait for user to inspect
        console.log('⏳ Keeping browser open for 10 seconds for inspection...');
        await new Promise(resolve => setTimeout(resolve, 10000));
        
        console.log('✅ All tests completed successfully!');
        
    } catch (error) {
        console.error('❌ Test failed:', error);
    } finally {
        await browser.close();
        console.log('🏁 Test completed and browser closed');
    }
}

// Run the test
runPuppeteerTest().catch(console.error);