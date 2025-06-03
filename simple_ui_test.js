const puppeteer = require('puppeteer');
const path = require('path');

async function simpleUITest() {
    console.log('🧪 Starting Simple UI test with Puppeteer...');
    
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 800 });
    
    try {
        // Navigate to our test HTML
        const htmlPath = path.resolve(__dirname, 'ui_test.html');
        await page.goto(`file://${htmlPath}`);
        
        console.log('✅ Page loaded successfully');
        
        // Test 1: Check if key UI elements exist
        const elements = await page.evaluate(() => {
            return {
                welcomePanel: !!document.getElementById('welcome-panel'),
                helpPanel: !!document.getElementById('help-panel'),
                codeOutput: !!document.getElementById('code-output'),
                codeError: !!document.getElementById('code-error'),
                userInput: !!document.getElementById('user-input'),
                title: document.querySelector('.title')?.textContent || '',
                greenElements: document.querySelectorAll('.green').length,
                blueElements: document.querySelectorAll('.blue').length,
                yellowElements: document.querySelectorAll('.yellow').length
            };
        });
        
        console.log('UI Elements Check:');
        console.log(`✅ Welcome Panel: ${elements.welcomePanel}`);
        console.log(`✅ Help Panel: ${elements.helpPanel}`);
        console.log(`✅ Code Output: ${elements.codeOutput}`);
        console.log(`✅ Code Error: ${elements.codeError}`);
        console.log(`✅ User Input: ${elements.userInput}`);
        console.log(`✅ Title: ${elements.title}`);
        console.log(`✅ Green Elements: ${elements.greenElements}`);
        console.log(`✅ Blue Elements: ${elements.blueElements}`);
        console.log(`✅ Yellow Elements: ${elements.yellowElements}`);
        
        // Test 2: Check CSS styling
        const styles = await page.evaluate(() => {
            const body = document.body;
            const terminal = document.querySelector('.terminal');
            const welcomePanel = document.querySelector('.welcome-panel');
            
            return {
                bodyBg: window.getComputedStyle(body).backgroundColor,
                terminalBorder: window.getComputedStyle(terminal).border,
                welcomePanelBorder: window.getComputedStyle(welcomePanel).border
            };
        });
        
        console.log('\nStyling Check:');
        console.log(`✅ Body Background: ${styles.bodyBg}`);
        console.log(`✅ Terminal Border: ${styles.terminalBorder}`);
        console.log(`✅ Welcome Panel Border: ${styles.welcomePanelBorder}`);
        
        // Test 3: Take screenshot
        await page.screenshot({ 
            path: 'simple_ui_test_screenshot.png', 
            fullPage: true 
        });
        console.log('✅ Screenshot saved as simple_ui_test_screenshot.png');
        
        // Test 4: Check responsiveness
        await page.setViewport({ width: 800, height: 600 });
        await page.screenshot({ 
            path: 'ui_test_responsive.png', 
            fullPage: true 
        });
        console.log('✅ Responsive screenshot saved as ui_test_responsive.png');
        
        console.log('\n🎉 Simple UI test completed successfully!');
        
    } catch (error) {
        console.error('❌ Test failed:', error);
    } finally {
        await browser.close();
    }
}

simpleUITest().catch(console.error);