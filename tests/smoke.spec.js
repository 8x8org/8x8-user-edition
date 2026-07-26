// @ts-check
/**
 * Smoke tests for the 8x8 OS Public Beta static cockpit.
 *
 * Exercises only the local static app:
 *   1. Page loads and exposes core UI elements.
 *   2. The service worker registers successfully.
 *   3. View-switch nav buttons mutate only local UI – no outbound requests.
 */
const { test, expect } = require('@playwright/test');

test('page loads with correct title and navigation', async ({ page }) => {
  await page.goto('/');

  await expect(page).toHaveTitle(/8x8 OS/);

  // At least one nav button is visible
  const firstNav = page.locator('[data-view]').first();
  await expect(firstNav).toBeVisible();

  // The overview section starts active
  await expect(page.locator('#overview')).toHaveClass(/active/);
});

test('service worker registers', async ({ page }) => {
  await page.goto('/');

  // navigator.serviceWorker.ready resolves once an active SW controls the page.
  // The app registers sw.js on the load event with skipWaiting, so this should
  // settle quickly on a local test server.
  const scope = await page.evaluate(() => {
    if (!('serviceWorker' in navigator)) return null;
    return navigator.serviceWorker.ready.then(reg => reg.scope);
  });

  expect(scope).toBeTruthy();
});

test('view-switch buttons mutate only local UI with no outbound requests', async ({ page, baseURL }) => {
  // Collect any cross-origin requests that occur while exercising the nav.
  const externalURLs = [];
  const localOrigin = new URL(/** @type {string} */ (baseURL)).origin;

  page.on('request', request => {
    try {
      if (!request.url().startsWith(localOrigin)) {
        externalURLs.push(request.url());
      }
    } catch {
      // non-http scheme (e.g. data:) – safe to ignore
    }
  });

  await page.goto('/');

  // Click through every nav view and confirm the correct section becomes active.
  const navViews = ['agents', 'map', 'roadmap', 'security', 'overview'];
  for (const view of navViews) {
    await page.click(`[data-view="${view}"]`);
    await expect(page.locator(`#${view}`)).toHaveClass(/active/);
  }

  // No cross-origin requests should have been made.
  expect(externalURLs, `Unexpected outbound request(s): ${externalURLs.join(', ')}`).toHaveLength(0);
});
