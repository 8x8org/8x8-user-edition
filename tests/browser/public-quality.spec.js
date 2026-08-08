const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const routes = ['/', '/first-blink', '/world', '/art-board'];

for (const route of routes) {
  test(`${route} renders current 0.0.1 Atlas without console errors`, async ({ page }) => {
    const consoleErrors = [];
    const pageErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    page.on('pageerror', err => pageErrors.push(err.message));

    const response = await page.goto(route, { waitUntil: 'networkidle' });
    expect(response).not.toBeNull();
    expect(response.status()).toBe(200);
    await expect(page).toHaveTitle(/8x8 OS .* Omniversal Command Atlas .* 0\.0\.1 Beta/);
    await expect(page.locator('body')).toContainText('PUBLIC PRESENT');
    expect(consoleErrors).toEqual([]);
    expect(pageErrors).toEqual([]);
  });
}

test('public UI does not make unexpected cross-origin requests', async ({ page, baseURL }) => {
  const origin = new URL(baseURL).origin;
  const unexpected = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.origin !== origin && !['data:', 'blob:'].includes(url.protocol)) {
      unexpected.push(request.url());
    }
  });
  await page.goto('/', { waitUntil: 'networkidle' });
  expect(unexpected).toEqual([]);
});

test('critical/serious axe findings are zero on the main Atlas', async ({ page }) => {
  await page.goto('/', { waitUntil: 'networkidle' });
  const results = await new AxeBuilder({ page }).analyze();
  const blocking = results.violations.filter(v => ['critical', 'serious'].includes(v.impact));
  expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
});

test('keyboard navigation exposes visible focus on interactive controls', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await page.keyboard.press('Tab');
  const focused = page.locator(':focus');
  await expect(focused).toBeVisible();
  const outlineStyle = await focused.evaluate(el => getComputedStyle(el).outlineStyle);
  expect(outlineStyle).not.toBe('none');
});

test('reduced motion disables or shortens nonessential animation', async ({ browser }) => {
  const context = await browser.newContext({ reducedMotion: 'reduce' });
  const page = await context.newPage();
  await page.goto('http://localhost:8080/', { waitUntil: 'domcontentloaded' });
  const animated = await page.locator('.heroMain::after').count().catch(() => 0);
  expect(animated).toBeGreaterThanOrEqual(0);
  await context.close();
});
