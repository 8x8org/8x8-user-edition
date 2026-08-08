const { defineConfig, devices } = require('@playwright/test');

const host = '127.0.0.1';
const port = 8080;

module.exports = defineConfig({
  testDir: './tests/browser',
  timeout: 30000,
  expect: { timeout: 5000 },
  fullyParallel: false,
  retries: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: `http://${host}:${port}`,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium-desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'chromium-mobile', use: { ...devices['Pixel 7'] } },
  ],
  webServer: {
    command: `python3 -m http.server ${port} --bind ${host}`,
    url: `http://${host}:${port}/stable/index.html`,
    reuseExistingServer: !process.env.CI,
    timeout: 30000,
  },
});
