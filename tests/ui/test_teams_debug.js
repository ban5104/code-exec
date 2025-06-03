const puppeteer = require('puppeteer');
const path = require('path');

async function debugTest() {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 800 });
    
    try {
        const url = `file://${path.resolve(__dirname, 'teams-cards-demo.html')}`;
        console.log('Loading URL:', url);
        
        await page.goto(url, { waitUntil: 'domcontentloaded' });
        
        // Take immediate screenshot
        await page.screenshot({ 
            path: path.join(__dirname, 'debug_initial.png'),
            fullPage: true 
        });
        
        // Check if elements exist
        const hasContainer = await page.$('#card-container') !== null;
        const hasButtons = await page.$$eval('button', buttons => buttons.length);
        const containerHTML = await page.$eval('#card-container', el => el.innerHTML);
        
        console.log('Has container:', hasContainer);
        console.log('Number of buttons:', hasButtons);
        console.log('Container HTML:', containerHTML.substring(0, 100) + '...');
        
        // Try clicking first button
        if (hasButtons > 0) {
            await page.click('button');
            await page.waitForTimeout(1000);
            
            await page.screenshot({ 
                path: path.join(__dirname, 'debug_after_click.png'),
                fullPage: true 
            });
            
            const afterClickHTML = await page.$eval('#card-container', el => el.innerHTML);
            console.log('After click HTML:', afterClickHTML.substring(0, 100) + '...');
        }
        
    } catch (error) {
        console.error('Debug error:', error);
    } finally {
        await browser.close();
    }
}

debugTest();