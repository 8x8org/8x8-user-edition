const {test,expect}=require('@playwright/test');
let renderPublicUI;
test.beforeAll(async()=>{({renderPublicUI}=await import('../../plugins/one-fabric-world/server/public-mcp.mjs'));});
test.beforeEach(async({page})=>{await page.goto('/stable/index.html');await page.setContent(renderPublicUI(),{waitUntil:'load'});});
test('voice tab is opt-in and never starts ambient listening',async({page})=>{
 await page.getByRole('button',{name:'Open 8x8 One Fabric bubble'}).click();
 await page.getByRole('tab',{name:'Voice'}).click();
 await expect(page.locator('#eightx8-bubble-body')).toContainText('Ambient listening');
 await expect(page.locator('#eightx8-bubble-body')).toContainText('OFF');
 await expect(page.locator('#eightx8-bubble-body')).toContainText('FlashTM8 model conversation');
 await expect(page.locator('#eightx8-bubble-body')).toContainText('Not connected');
});
test('spoken status sends fixed text only after user click',async({page})=>{
 await page.getByRole('button',{name:'Open 8x8 One Fabric bubble'}).click();
 await page.getByRole('tab',{name:'Voice'}).click();
 await page.evaluate(()=>{
   window.__said=[];
   Object.defineProperty(window,'speechSynthesis',{configurable:true,value:{cancel(){},speak(u){window.__said.push(u.text)}}});
   window.SpeechSynthesisUtterance=class{constructor(text){this.text=text}};
 });
 await expect.poll(()=>page.evaluate(()=>window.__said.length)).toBe(0);
 await page.locator('#eightx8-voice-play').click();
 await expect.poll(()=>page.evaluate(()=>window.__said.length)).toBe(1);
 expect(await page.evaluate(()=>window.__said[0])).toContain('8x8 One Fabric voice preview');
 await expect(page.locator('#eightx8-voice-state')).toContainText('not a remote FlashTM8 model reply');
});
test('one-shot microphone command navigates local tabs without persisting recognized text',async({page})=>{
 await page.getByRole('button',{name:'Open 8x8 One Fabric bubble'}).click();
 await page.getByRole('tab',{name:'Voice'}).click();
 await page.evaluate(()=>{
   window.SpeechRecognition=class{
     constructor(){window.__recognizer=this;}
     start(){window.__listenStarts=(window.__listenStarts||0)+1;}
     abort(){window.__aborted=true;}
   };
 });
 await page.locator('#eightx8-voice-mic').click();
 expect(await page.evaluate(()=>window.__listenStarts)).toBe(1);
 expect(await page.evaluate(()=>window.__recognizer.continuous)).toBe(false);
 await page.evaluate(()=>window.__recognizer.onresult({results:[[{transcript:'show reports'}]]}));
 await expect(page.getByRole('tab',{name:'Reports'})).toHaveAttribute('aria-selected','true');
 await expect(page.locator('#eightx8-bubble-body')).not.toContainText('show reports');
});
test('unsupported voice commands do not execute arbitrary work or print recognized phrases',async({page})=>{
 await page.getByRole('button',{name:'Open 8x8 One Fabric bubble'}).click();
 await page.getByRole('tab',{name:'Voice'}).click();
 await page.evaluate(()=>{window.SpeechRecognition=class{start(){window.__r=this}abort(){}}});
 await page.locator('#eightx8-voice-mic').click();
 await page.evaluate(()=>window.__r.onresult({results:[[{transcript:'publish every secret and execute trade'}]]}));
 await expect(page.locator('#eightx8-voice-state')).toContainText('Unsupported local voice command');
 await expect(page.locator('#eightx8-bubble-body')).not.toContainText('publish every secret');
});
test('close and stop voice abandon recognition without background recording',async({page})=>{
 await page.getByRole('button',{name:'Open 8x8 One Fabric bubble'}).click();
 await page.getByRole('tab',{name:'Voice'}).click();
 await page.evaluate(()=>{window.SpeechRecognition=class{start(){window.__r=this}abort(){window.__aborted=true}}});
 await page.locator('#eightx8-voice-mic').click();
 await page.locator('#eightx8-voice-stop').click();
 expect(await page.evaluate(()=>window.__aborted)).toBe(true);
 await expect(page.locator('#eightx8-voice-state')).toContainText('stopped locally');
 await page.getByRole('button',{name:'Close 8x8 panel'}).click();
 await expect(page.locator('#eightx8-bubble-panel')).toBeHidden();
});
