const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const stablePath = '/stable/index.html';

test('stable client renders 0.1.0 Living Fabric without console errors', async ({ page }) => {
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', err => pageErrors.push(err.message));

  const response = await page.goto(stablePath, { waitUntil: 'networkidle' });
  expect(response).not.toBeNull();
  expect(response.status()).toBe(200);
  await expect(page).toHaveTitle(/8x8 OS .* Living Omniversal Gate R4 .* 0\.1\.0 Stable/);
  await expect(page.locator('body')).toContainText('0.1.0 STABLE');
  await expect(page.locator('#enter')).toBeVisible();
  expect(consoleErrors).toEqual([]);
  expect(pageErrors).toEqual([]);
});

test('opening Gate enters the stable Living Fabric', async ({ page }) => {
  await page.goto(stablePath, { waitUntil: 'domcontentloaded' });
  await page.locator('#enter').click();
  await expect(page.locator('#gate')).toHaveClass(/open/);
  await expect(page.locator('#home')).toHaveClass(/active/);
});

test('1D through 8D projection controls are interactive', async ({ page }) => {
  await page.goto(stablePath, { waitUntil: 'domcontentloaded' });
  await page.locator('#enter').click();
  for (let dim = 1; dim <= 8; dim += 1) {
    await page.locator(`[data-dim="${dim}"]`).click();
    await expect(page.locator('#dimTitle')).toContainText(`${dim}D`);
  }
});

test('R3 rollback source remains renderable', async ({ page }) => {
  const response = await page.goto('/index.html', { waitUntil: 'networkidle' });
  expect(response).not.toBeNull();
  expect(response.status()).toBe(200);
  await expect(page).toHaveTitle(/8x8 OS .* Living Omniversal Gate R3 .* 0\.0\.1 Beta/);
});

test('stable public UI does not make unexpected cross-origin requests', async ({ page, baseURL }) => {
  const origin = new URL(baseURL).origin;
  const unexpected = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.origin !== origin && !['data:', 'blob:'].includes(url.protocol)) unexpected.push(request.url());
  });
  await page.goto(stablePath, { waitUntil: 'networkidle' });
  expect(unexpected).toEqual([]);
});

test('critical and serious axe findings are zero on the stable Living Fabric', async ({ page }) => {
  await page.goto(stablePath, { waitUntil: 'networkidle' });
  const results = await new AxeBuilder({ page }).analyze();
  const blocking = results.violations.filter(v => ['critical', 'serious'].includes(v.impact));
  expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
});

test('visible primary navigation has a focus treatment', async ({ page }) => {
  await page.goto(stablePath, { waitUntil: 'domcontentloaded' });
  await page.locator('#enter').click();
  const control = page.locator('.topnav button:visible').first();
  const count = await control.count();
  test.skip(count === 0, 'Desktop nav is intentionally collapsed in this viewport; mobile accessibility is covered by axe and route gates.');
  await control.focus();
  await expect(control).toBeFocused();
  const borderColor = await control.evaluate(el => getComputedStyle(el).borderColor);
  expect(borderColor).not.toBe('rgba(0, 0, 0, 0)');
  expect(borderColor).not.toBe('transparent');
});
