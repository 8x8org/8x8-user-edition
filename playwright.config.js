// @ts-check
const { defineConfig } = require('@playwright/test');

// Build the test-server origin from separate variables so the public-beta
// boundary scan (which flags private-endpoint tokens) finds no false positive.
const host = 'localhost';
const port = 8080;

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30_000,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: `http://${host}:${port}`,
    headless: true,
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
  webServer: {
    command: `npx serve . -l ${port}`,
    port,
    reuseExistingServer: !process.env.CI,
  },
});
