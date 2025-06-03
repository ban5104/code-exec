# Puppeteer MCP Server - Installation Guide

The Puppeteer MCP server requires Chrome/Chromium and its dependencies to be installed. Since we encountered a missing `libnss3.so` library error, here are the solutions:

## Option 1: Install System Dependencies (Recommended)
Run the following command with sudo privileges:

```bash
sudo apt-get update && sudo apt-get install -y \
  libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
  libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
  libxrandr2 libgbm1 libasound2 libatspi2.0-0 libgtk-3-0
```

## Option 2: Use Firefox Instead
Puppeteer can work with Firefox which might have fewer dependency issues:

```bash
PUPPETEER_PRODUCT=firefox npm install puppeteer
```

## Option 3: Use Docker
Run Chrome in a Docker container:

```bash
docker run -d -p 9222:9222 --cap-add=SYS_ADMIN \
  zenika/alpine-chrome:latest \
  --no-sandbox --remote-debugging-address=0.0.0.0 \
  --remote-debugging-port=9222
```

Then configure Puppeteer to connect to it:
```javascript
const browser = await puppeteer.connect({
  browserWSEndpoint: 'ws://localhost:9222/devtools/browser/...'
});
```

## Option 4: Use puppeteer-core with Existing Chrome
If you have Chrome installed elsewhere:

```bash
npm install puppeteer-core
```

Then specify the Chrome executable path:
```javascript
const browser = await puppeteer.launch({
  executablePath: '/path/to/chrome'
});
```

## Testing
After installation, test with:

```javascript
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.goto('https://example.com');
  console.log('Title:', await page.title());
  await browser.close();
})();
```