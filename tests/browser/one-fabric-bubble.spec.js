const {test,expect}=require('@playwright/test');
let renderPublicUI,renderObservatoryUI;
test.beforeAll(async()=>{({renderPublicUI,renderObservatoryUI}=await import('../../plugins/one-fabric-world/server/public-mcp.mjs'));});
test.beforeEach(async({page})=>{await page.goto('/stable/index.html');await page.setContent(renderPublicUI(),{waitUntil:'load'});});
test('bubble toggles and reports no live service',async({page})=>{
 const b=page.getByRole('button',{name:'Open 8x8 One Fabric bubble'});
 await expect(b).toBeVisible();await b.click();
 await expect(b).toHaveAttribute('aria-expanded','true');
 await expect(page.locator('#eightx8-bubble-body')).toContainText('Not established');
 await page.getByRole('button',{name:'Close 8x8 panel'}).click();
 await expect(b).toHaveAttribute('aria-expanded','false');
});
test('reports deny false run receipts',async({page})=>{
 await page.getByRole('button',{name:'Open 8x8 One Fabric bubble'}).click();
 await page.getByRole('tab',{name:'Reports'}).click();
 await expect(page.locator('#eightx8-bubble-body')).toContainText('Not instrumented');
 await expect(page.locator('#eightx8-bubble-body')).toContainText('No authenticated feed');
});
test('access tab has no credential intake and Escape closes',async({page})=>{
 await page.getByRole('button',{name:'Open 8x8 One Fabric bubble'}).click();
 await page.getByRole('tab',{name:'Access'}).click();
 await expect(page.locator('#eightx8-bubble-body')).toContainText('Do not paste API keys');
 await expect(page.locator('#eightx8-bubble-panel input')).toHaveCount(0);
 await page.keyboard.press('Escape');
 await expect(page.locator('#eightx8-bubble-panel')).toBeHidden();
});
test('Observatory includes one shared bubble',async({page})=>{
 await page.setContent(renderObservatoryUI(),{waitUntil:'load'});
 await expect(page.locator('#eightx8-bubble-root')).toHaveCount(1);
 await page.getByRole('button',{name:'Open 8x8 One Fabric bubble'}).click();
 await expect(page.locator('#eightx8-bubble-body')).toContainText('No provider-connected LIVE indicator');
});
test('Android native bubble lacks global overlay powers',async()=>{
 const {readFileSync}=require('node:fs');const root=require('node:path').resolve(__dirname,'../..');
 const java=readFileSync(root+'/android-app/app/src/main/java/world/eightx8/user/MainActivity.java','utf8');
 const manifest=readFileSync(root+'/android-app/app/src/main/AndroidManifest.xml','utf8');
 expect(java).toContain('showPanel()');expect(java).toContain('hidePanel()');
 expect(java).toContain('onPause()');
 expect(manifest).not.toContain('SYSTEM_ALERT_WINDOW');
});
test('Android and Telegram web carriers reference shared asset',async()=>{
 const {readFileSync}=require('node:fs');const root=require('node:path').resolve(__dirname,'../..');
 for(const p of ['android/index.html','telegram/index.html']){expect(readFileSync(root+'/'+p,'utf8')).toContain('/assets/8x8-bubble.js');}
});
