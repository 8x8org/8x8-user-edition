const { test, expect }=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
test('8x8 free-preview event shows explicit finite scope and voluntary payment',async ({page})=>{
 await page.goto('/open-world-2026');
 await expect(page.getByRole('heading',{level:1})).toContainText('Open World');
 await expect(page.getByText('November 1 – December 31, 2026')).toBeVisible();
 await expect(page.getByText(/not confirmation of a live production launch/i)).toBeVisible();
 await expect(page.getByRole('link',{name:/Support 8x8 — optional/})).toHaveAttribute('href',/^https:\/\/buy\.stripe\.com\//);
 await expect(page.getByText(/No paid subscription will be automatically started/i)).toBeVisible();
 await expect(page.getByText(/No NFT, token allocation/i)).toBeVisible();
});
test('free-preview announcement is not blocked by major accessibility violations',async ({page})=>{
 await page.goto('/open-world-2026');
 const report=await new AxeBuilder({page}).analyze();
 const blocking=report.violations.filter(v=>['serious','critical'].includes(v.impact));
 expect(blocking,JSON.stringify(blocking,null,2)).toEqual([]);
});