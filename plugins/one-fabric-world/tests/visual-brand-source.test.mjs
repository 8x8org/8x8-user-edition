import test from 'node:test';
import assert from 'node:assert/strict';
import {
  renderPublicUI, renderObservatoryUI, renderAgentTheaterUI,
  getPublicConceptAvatarSummary,
} from '../server/public-mcp.mjs';

test('four existing theater artworks are reused as concept avatars, not live agent claims',()=>{
 const cast=getPublicConceptAvatarSummary();
 assert.equal(cast.length,4);
 assert.equal(new Set(cast.map(x=>x.id)).size,4);
 assert.ok(cast.every(x=>x.evidence_state==='ORIGINAL_CONCEPT_NOT_AUTHENTICATED'));
 assert.ok(cast.every(x=>x.name.length>1&&x.role.length>0));
});
test('all three MCP Apps resources contain a recognizable red black 8x8 mark and gallery',()=>{
 for(const html of [renderPublicUI(),renderAgentTheaterUI(),renderObservatoryUI()]){
   assert.match(html,/Red and black 8x8 brand mark/);
   assert.match(html,/eightx8-brand-mark/);
   assert.match(html,/#e73c4d/);
   assert.match(html,/data-eightx8-brand-mark/);
   assert.match(html,/eightx8-agent-gallery/);
   assert.match(html,/Original character concepts only/);
 }
});
test('MCP rendering contains the actual recovered embedded WebP portraits, no remote image dependency',()=>{
 const html=renderPublicUI();
 const match=html.match(/window\.__EIGHTX8_PUBLIC_CONCEPT_AVATARS__=(\[[^\n]+\]);/);
 assert.ok(match,'avatar data bootstrap missing');
 const cast=JSON.parse(match[1]);
 assert.equal(cast.length,4);
 assert.ok(cast.every(x=>/^data:image\/webp;base64,[A-Za-z0-9+/=]+$/.test(x.portrait)));
 assert.ok(cast.every(x=>x.portrait.length<55000));
});
test('UI banner and media functionality still coexist with avatar stage',()=>{
 const hub=renderPublicUI();
 assert.match(hub,/Your 8x8 World/);
 assert.match(hub,/Local 8x8 video preview/);
 assert.match(hub,/One sovereign capability graph/);
 const theater=renderAgentTheaterUI();
 assert.match(theater,/Cinematic Agent Theater/);
 assert.match(theater,/SOURCE CONCEPT/);
 assert.match(renderObservatoryUI(),/Living Observatory/);
});
test('in-page bubble never fabricates auth, device, model or publishing abilities',()=>{
 const html=renderPublicUI();
 assert.match(html,/No provider-connected LIVE indicator/);
 assert.ok(html.includes('Background 24/7'));
 assert.match(html,/Ambient listening/);
 assert.match(html,/Direct publishing/);
 assert.match(html,/This public preview cannot collect credentials/);
 assert.ok(!html.includes('<video autoplay'));
});
