const { test, expect } = require('@playwright/test');

test('public atlas remains readable and exposes 64 server-rendered topic cards', async ({ page }) => {
  await page.goto('/projects/world-atlas/index.html');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('One world.');
  await expect(page.locator('.realm')).toHaveCount(8);
  await expect(page.locator('.topic')).toHaveCount(64);
  await expect(page.getByRole('link', { name: /8x8 home/i })).toBeVisible();
  await expect(page.getByText(/topic label does not indicate an active service/i).first()).toBeVisible();
});

test('public atlas search filters real semantic topic cards without inventing tools', async ({ page }) => {
  await page.goto('/projects/world-atlas/index.html');
  const search = page.getByRole('searchbox', { name: 'Find a topic in the 8x8 World' });
  await search.fill('nuclear');
  await expect(page.locator('.topic:visible')).toHaveCount(1);
  await expect(page.getByText('Nuclear energy research', { exact: true })).toBeVisible();
  await expect(page.locator('#counter')).toContainText('1 of 64');
  await search.fill('a topic that is not in the atlas');
  await expect(page.locator('.topic:visible')).toHaveCount(0);
  await expect(page.locator('#noresults')).toBeVisible();
  await search.fill('');
  await expect(page.locator('.topic:visible')).toHaveCount(64);
});
