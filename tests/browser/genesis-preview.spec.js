const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
test('Genesis page is educational and offers no token checkout',async({page})=>{
 await page.goto('/projects/open-world-2026/genesis.html');
 await expect(page.getByRole('heading',{level:1})).toContainText('Genesis');
 await expect(page.getByText(/No token sale or reservation checkout is open/i)).toBeVisible();
 await expect(page.getByText(/not.*market price/i).first()).toBeVisible();
 await page.getByRole('button',{name:'Preview wallet connection'}).click();
 await expect(page.locator('#wallet-result')).toContainText('No compatible injected wallet');
 await expect(page.getByRole('link',{name:/Support the 8x8 project/})).toHaveAttribute('href',/^https:\/\/buy\.stripe\.com\//);
});
test('Wallet connect requests account exposure only when clicked',async({page})=>{
 await page.addInitScript(()=>{window.__requested=[];window.ethereum={request:async({method})=>{window.__requested.push(method);if(method==='eth_requestAccounts')return ['0x1234567890123456789012345678901234567890'];throw Error('Unexpected method')}}});
 await page.goto('/projects/open-world-2026/genesis.html');
 expect(await page.evaluate(()=>window.__requested)).toEqual([]);
 await page.getByRole('button',{name:'Preview wallet connection'}).click();
 await expect(page.locator('#wallet-result')).toContainText('0x123456…567890');
 expect(await page.evaluate(()=>window.__requested)).toEqual(['eth_requestAccounts']);
 await page.getByRole('button',{name:'Clear displayed wallet'}).click();
 await expect(page.locator('#wallet-result')).toContainText('Displayed wallet cleared');
});
test('Genesis preview has no serious or critical accessibility violations',async({page})=>{
 await page.goto('/projects/open-world-2026/genesis.html');
 const report=await new AxeBuilder({page}).analyze();
 expect(report.violations.filter(v=>['serious','critical'].includes(v.impact))).toEqual([]);
});