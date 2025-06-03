#!/bin/bash

echo "Installing Puppeteer dependencies..."

# Create a list of required packages
PACKAGES="
libnss3
libnspr4
libatk1.0-0
libatk-bridge2.0-0
libcups2
libdrm2
libxkbcommon0
libxcomposite1
libxdamage1
libxfixes3
libxrandr2
libgbm1
libasound2
libatspi2.0-0
libgtk-3-0
"

echo "Required packages for Chrome/Chromium:"
echo "$PACKAGES"

echo ""
echo "To install these packages, run:"
echo "sudo apt-get update && sudo apt-get install -y $PACKAGES"

echo ""
echo "Alternatively, you can try using Puppeteer with Firefox instead:"
echo "PUPPETEER_PRODUCT=firefox npm install puppeteer"

echo ""
echo "Or use puppeteer-core with an existing Chrome installation:"
echo "npm install puppeteer-core"

# Check current environment
echo ""
echo "Current environment check:"
echo "========================="
echo "Node version: $(node --version 2>/dev/null || echo 'Not found')"
echo "NPM version: $(npm --version 2>/dev/null || echo 'Not found')"

# Try to find Chrome/Chromium
echo ""
echo "Looking for Chrome/Chromium installations:"
for chrome in google-chrome chromium-browser chromium chrome; do
    if command -v $chrome &> /dev/null; then
        echo "Found: $(which $chrome)"
        $chrome --version 2>/dev/null || echo "  (version check failed)"
    fi
done

echo ""
echo "Checking LD_LIBRARY_PATH:"
echo "$LD_LIBRARY_PATH"

echo ""
echo "To test Puppeteer after installing dependencies, create a test file:"
cat << 'EOF'

// test_puppeteer.js
const puppeteer = require('puppeteer');

(async () => {
  try {
    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    await page.goto('https://example.com');
    console.log('Title:', await page.title());
    await browser.close();
  } catch (error) {
    console.error('Error:', error.message);
  }
})();
EOF