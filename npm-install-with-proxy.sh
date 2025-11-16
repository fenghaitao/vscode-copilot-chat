#!/bin/bash

# Install npm packages (skip Playwright browser download)
echo "Installing npm packages..."
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
npm install

# Install Playwright browsers with proxy
echo "Installing Playwright Chromium browser..."
npx playwright install chromium

echo "Installation complete!"
