const {test,expect}=require('@playwright/test');
let renderObservatoryUI;
test.beforeAll(async()=>{
 ({renderObservatoryUI}=await import('../../plugins/one-fabric-world/server/public-mcp.mjs'));
});
test.beforeEach(async({page})=>{
 await page.goto('/stable/index.html');
 await page.setContent(renderObservatoryUI(),{waitUntil:'load'});
});
test('observatory has 24 interactive domains and never claims real agent attendance',async({page})=>{
 await expect(page.getByRole('heading',{name:'The Living Observatory'})).toBeVisible();
 await expect(page.locator('#domains button')).toHaveCount(24);
 await expect(page.getByText('0',{exact:true}).last()).toBeVisible();
 await expect(page.locator('#source-indicator')).toContainText('No live owner event stream');
 await page.locator('#domains button').nth(6).click();
 await expect(page.locator('#domain-detail')).toContainText('Jarvis');
 await expect(page.locator('#domain-detail')).toContainText('No live implementation inferred');
});
test('playing an agent work animation labels every event as illustration',async({page})=>{
 await page.getByRole('button',{name:'Play workflow illustration'}).click();
 await expect(page.locator('#scene')).toHaveClass(/playing/);
 await expect(page.locator('#events li')).toHaveCount(8,{timeout:12000});
 await expect(page.locator('#event-status')).toContainText('zero external actions');
 await expect(page.locator('#events')).toContainText('not a verified model response');
});
test('reset hides visual playback and returns to no-feed state',async({page})=>{
 await page.getByRole('button',{name:'Play workflow illustration'}).click();
 await page.getByRole('button',{name:'Reset illustration'}).click();
 await expect(page.locator('#events li')).toHaveCount(2);
 await expect(page.locator('#event-status')).toContainText('No live events collected');
 await expect(page.locator('#scene')).not.toHaveClass(/playing/);
});
