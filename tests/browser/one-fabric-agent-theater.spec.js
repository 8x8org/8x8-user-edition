const {test,expect}=require('@playwright/test');
let renderAgentTheaterUI;
test.beforeAll(async()=>{
  ({renderAgentTheaterUI}=await import('../../plugins/one-fabric-world/server/public-mcp.mjs'));
});
test.beforeEach(async({page})=>{
  await page.goto('/stable/index.html');
  await page.setContent(renderAgentTheaterUI(),{waitUntil:'load'});
});
test('restored original cinematic portraits and ChatGPT connector are source-labeled',async({page})=>{
  await expect(page.getByRole('heading',{name:/Agents that look, speak and work/})).toBeVisible();
  await expect(page.locator('#rail button')).toHaveCount(8);
  await expect(page.locator('#rail img')).toHaveCount(7);
  await expect(page.locator('#indexcount')).toContainText('212 total historical');
  await expect(page.locator('.toplabel')).toContainText('NO LIVE MODEL SESSIONS');
  await page.locator('#rail button').nth(3).click();
  await expect(page.locator('#agent')).toHaveText('Jarvis');
  await page.locator('#rail button').nth(7).click();
  await expect(page.locator('#agent')).toHaveText('ChatGPT Bridge');
  await expect(page.locator('#runtime')).toContainText('no authenticated model session');
});
test('multi-agent example is explicitly scripted and executes nothing',async({page})=>{
  await page.locator('#demo').click();
  await expect(page.locator('#transcript .entry')).toHaveCount(4);
  await expect(page.locator('#transcript')).toContainText('SCRIPTED SCENARIO');
  await expect(page.locator('#runtime')).toContainText('No genuine agent dialogue');
});
test('voice playback is started only by a user gesture',async({page})=>{
  await page.evaluate(()=>{
    window.__utterances=[];
    Object.defineProperty(window,'speechSynthesis',{configurable:true,value:{
      cancel(){},speak(u){window.__utterances.push(u.text)}
    }});
    window.SpeechSynthesisUtterance=class{constructor(t){this.text=t}};
  });
  expect(await page.evaluate(()=>window.__utterances.length)).toBe(0);
  await page.locator('#play').click();
  await expect.poll(()=>page.evaluate(()=>window.__utterances.length)).toBe(1);
  expect(await page.evaluate(()=>window.__utterances[0])).toContain('no real model session');
  await expect(page.locator('#speaker')).toContainText('browser text-to-speech demo');
  await page.locator('#stop').click();
  await expect(page.locator('#runtime')).toContainText('Speech stopped locally');
});
test('new local work request is not transmitted or exposed as task execution',async({page})=>{
  await page.locator('#input').fill('please inspect a project');
  await page.locator('#stage').click();
  await expect(page.locator('#input')).toHaveValue('');
  await expect(page.locator('#transcript')).toContainText('UNSENT DRAFT');
  await expect(page.locator('#transcript')).not.toContainText('please inspect a project');
});
test('all historic identities are searchable without claiming their voices',async({page})=>{
  await page.locator('#search').fill('ARCHON');
  await expect(page.locator('#directory button')).toHaveCount(1);
  await page.locator('#directory button').first().click();
  await expect(page.locator('#runtime')).toContainText('registered historical source identity');
});
