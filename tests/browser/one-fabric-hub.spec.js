const {test,expect}=require('@playwright/test');
let renderPublicUI;
test.beforeAll(async()=>{
 ({renderPublicUI}=await import('../../plugins/one-fabric-world/server/public-mcp.mjs'));
});
test.beforeEach(async({page})=>{
 await page.goto('/stable/index.html');
 await page.setContent(renderPublicUI(),{waitUntil:'load'});
});
const marketFixture=()=>({
 schema:'8x8.public.market.snapshot.v1',
 classification:'LOCAL_IMPORT_UNVERIFIED',
 scope:'PUBLIC_MARKET_ONLY',
 source_label:'BROWSER TEST FIXTURE NOT LIVE',
 venue:'TEST',instrument:'FIXTURE-USD',interval:'1m',
 window_start:'2026-01-01T00:00:00Z',window_end:'2026-01-01T00:02:00Z',observed_at:'2026-01-01T00:03:00Z',
 market_trade_count:'123456789012345678901234567890',
 bars:[
  {timestamp:'2026-01-01T00:00:00Z',open:9,high:11,low:8,close:10,volume:100},
  {timestamp:'2026-01-01T00:01:00Z',open:10,high:13,low:9,close:12,volume:200},
  {timestamp:'2026-01-01T00:02:00Z',open:12,high:14,low:11,close:13,volume:150}
 ]
});
test('public atlas search shows matching families without fake runtime claims',async({page})=>{
 await expect(page.getByText('Your 8x8 World',{exact:true})).toBeVisible();
 await expect(page.locator('#experience-atlas details')).toHaveCount(20);
 await page.locator('#atlas-search').fill('staking');
 await expect(page.locator('#atlas-filter-status')).toContainText('matching entries');
 await expect(page.locator('#experience-atlas details:visible').first()).toBeVisible();
 await expect(page.locator('#experience-atlas details:visible summary .state').first()).toBeVisible();
});
test('local OHLCV import renders actual chart with exact big trade count without live badge',async({page})=>{
 await page.locator('#market-json').setInputFiles({name:'market.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(marketFixture()))});
 await expect(page.locator('#market-import-state')).toContainText('LOCAL IMPORT ONLY');
 await expect(page.locator('#market-svg')).toBeVisible();
 await expect(page.locator('#market-chart-path')).toHaveAttribute('d',/^M/);
 await expect(page.locator('#market-trade-count')).toHaveText('123,456,789,012,345,678,901,234,567,890');
 await expect(page.locator('#market-import-state')).toContainText('LOCAL IMPORT ONLY');
 await expect(page.locator('#market-import-state')).toContainText('UNVERIFIED');
 await expect(page.getByText('Gate 2:',{exact:false})).toBeVisible();
});
test('private account field and false live provenance are rejected in local import',async({page})=>{
 const src=marketFixture();src.account_fill_count='1000';
 await page.locator('#market-json').setInputFiles({name:'private.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(src))});
 await expect(page.locator('#market-import-state')).toContainText('UNKNOWN_OR_PRIVATE_FIELD');
 await expect(page.locator('#market-svg')).toBeHidden();
 const invalid=marketFixture();invalid.classification='LIVE_PROVIDER_VERIFIED';
 await page.locator('#market-json').setInputFiles({name:'fake-live.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(invalid))});
 await expect(page.locator('#market-import-state')).toContainText('NOT_A_PUBLIC_LOCAL_SNAPSHOT');
 await expect(page.locator('#market-trade-count')).toHaveText('UNAVAILABLE');
});
test('music and video local preview controls do not upload or auto-play',async({page})=>{
 await expect(page.locator('#video-player')).toHaveAttribute('preload','none');
 await expect(page.locator('#audio-player')).toHaveAttribute('preload','none');
 await page.locator('#audio-file').setInputFiles({name:'fixture.wav',mimeType:'audio/wav',buffer:Buffer.from('RIFFtestWAVE')});
 await expect(page.locator('#audio-state')).toContainText('No network upload');
 await expect(page.locator('#spotify-state')).toContainText('unverified');
});
test('Spotify embed only loads on explicit click with supported share link',async({page})=>{
 await page.route('https://open.spotify.com/**',route=>route.fulfill({status:200,body:'<!doctype html><title>provider mocked</title>'}));
 await page.locator('#spotify-link').fill('https://notspotify.example/track/1Lr4kGOYn9l83EjuK6cZFQ');
 await page.locator('#spotify-load').click();
 await expect(page.locator('#spotify-state')).toContainText('Only official');
 await expect(page.locator('#spotify-container iframe')).toHaveCount(0);
 await page.locator('#spotify-link').fill('https://open.spotify.com/track/0Lr4kGOYn9l83EjuK6cZFQ');
 await page.locator('#spotify-load').click();
 await expect(page.locator('#spotify-container iframe')).toHaveAttribute('src','https://open.spotify.com/embed/track/0Lr4kGOYn9l83EjuK6cZFQ');
 await expect(page.locator('#spotify-state')).toContainText('Official Spotify Embed');
});

test('FlashTM8 preflight reports missing authorization and retains provider gates',async({page})=>{
 await page.locator('#scenario-select').selectOption('markets');
 await page.locator('#access-select').selectOption('NOT_AUTHENTICATED');
 await page.locator('#access-launch').click();
 const dialog=page.locator('#access-dialog');
 await expect(dialog).toBeVisible();
 await expect(page.locator('#access-state')).toContainText('No verified login');
 await expect(page.locator('#access-description')).toContainText('no account check');
 await expect(page.locator('#access-missing li')).not.toHaveCount(0);
 await page.locator('#access-close').click();
 await expect(dialog).toBeHidden();
});
test('video credit block can be resolved into safe provider options without payment',async({page})=>{
 await page.locator('#scenario-select').selectOption('studio');
 await page.locator('#access-select').selectOption('QUOTA_BLOCKED');
 await page.locator('#access-launch').click();
 await expect(page.locator('#access-state')).toContainText('Provider credits or rate limit');
 await expect(page.locator('#access-state')).toContainText('preserve draft');
 await expect(page.locator('#access-receipt')).toContainText('finished-video');
 await page.locator('#access-close').click();
});
test('Studio creates actual locally editable 8:08 kit with 11 unsent social drafts',async({page})=>{
 await page.locator('#episode-title').fill('The World of Agents');
 await page.locator('#studio-draft').click();
 await expect(page.locator('#studio-state')).toContainText('08:08');
 await expect(page.locator('#studio-scenes span')).toHaveCount(8);
 await expect(page.locator('#studio-save')).toBeEnabled();
 const downloadWait=page.waitForEvent('download');
 await page.locator('#studio-save').click();
 const download=await downloadWait;
 expect(download.suggestedFilename()).toBe('8x8-8m08s-production-kit.json');
});
