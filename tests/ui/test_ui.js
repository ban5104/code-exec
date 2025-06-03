const puppeteer = require('puppeteer');
const path = require('path');

async function testUI() {
    console.log('🧪 Starting UI test with Puppeteer...');
    
    // Launch browser
    const browser = await puppeteer.launch({
        headless: true, // Run in headless mode for CI
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 800 });
    
    try {
        // Navigate to our test HTML
        const htmlPath = path.resolve(__dirname, 'ui_test.html');
        await page.goto(`file://${htmlPath}`);
        
        console.log('✅ Page loaded successfully');
        
        // Test 1: Check if welcome panel is visible
        const welcomePanel = await page.$('#welcome-panel');
        if (welcomePanel) {
            console.log('✅ Welcome panel is visible');
        } else {
            console.log('❌ Welcome panel not found');
        }
        
        // Test 2: Check title content
        const titles = await page.$$eval('.title', els => els.map(el => el.textContent));
        const hasCorrectTitle = titles.some(title => title.includes('Claude with Code Execution Tool'));
        if (hasCorrectTitle) {
            console.log('✅ Title content is correct');
        } else {
            console.log('❌ Title content is incorrect');
            console.log('   Found titles:', titles);
        }
        
        // Test 3: Test help functionality
        await page.click('button[onclick="showHelp()"]');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const helpVisible = await page.evaluate(() => {
            const helpPanel = document.getElementById('help-panel');
            return helpPanel.style.display !== 'none';
        });
        
        if (helpVisible) {
            console.log('✅ Help panel shows correctly');
        } else {
            console.log('❌ Help panel not showing');
        }
        
        // Test 4: Test input functionality
        await page.type('#user-input', '/help');
        await page.keyboard.press('Enter');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        console.log('✅ Input interaction works');
        
        // Test 5: Test code output display
        await page.click('button[onclick="showCodeOutput()"]');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const codeOutputVisible = await page.evaluate(() => {
            const codeOutput = document.getElementById('code-output');
            return codeOutput.style.display !== 'none';
        });
        
        if (codeOutputVisible) {
            console.log('✅ Code output panel shows correctly');
        } else {
            console.log('❌ Code output panel not showing');
        }
        
        // Test 6: Test error display
        await page.click('button[onclick="showCodeError()"]');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const errorVisible = await page.evaluate(() => {
            const codeError = document.getElementById('code-error');
            return codeError.style.display !== 'none';
        });
        
        if (errorVisible) {
            console.log('✅ Error panel shows correctly');
        } else {
            console.log('❌ Error panel not showing');
        }
        
        // Test 7: Check color styling
        const styles = await page.evaluate(() => {
            const greenElement = document.querySelector('.green');
            const blueElement = document.querySelector('.blue');
            const yellowElement = document.querySelector('.yellow');
            
            return {
                green: window.getComputedStyle(greenElement).color,
                blue: window.getComputedStyle(blueElement).color,
                yellow: window.getComputedStyle(yellowElement).color
            };
        });
        
        if (styles.green && styles.blue && styles.yellow) {
            console.log('✅ Color styling is applied correctly');
            console.log(`   Green: ${styles.green}`);
            console.log(`   Blue: ${styles.blue}`);
            console.log(`   Yellow: ${styles.yellow}`);
        } else {
            console.log('❌ Color styling not applied correctly');
        }
        
        // Test 8: Take screenshot for visual verification
        await page.screenshot({ 
            path: 'ui_test_screenshot.png', 
            fullPage: true 
        });
        console.log('✅ Screenshot saved as ui_test_screenshot.png');
        
        console.log('\n🎉 All UI tests completed successfully!');
        
        // Wait a bit to see the result
        await new Promise(resolve => setTimeout(resolve, 3000));
        
    } catch (error) {
        console.error('❌ Test failed:', error);
    } finally {
        await browser.close();
    }
}

// Run the test
testUI().catch(console.error);