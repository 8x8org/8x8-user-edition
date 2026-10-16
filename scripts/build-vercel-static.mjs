import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';

import { renderPublicUI, renderObservatoryUI, renderAgentTheaterUI } from '../plugins/one-fabric-world/server/public-mcp.mjs';

const out = 'dist';
rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

const items = [
  'v50.html',
  'index.html',
  'manifest.webmanifest',
  'one-fabric-capability-estate-v52.js',
  'one-fabric-interaction-estate-v53.js',
  'one-fabric-public-transparency-v54.js',
  'one-fabric-three-gate-experience-v55.js',
  'stable',
  'presale',
  'telegram',
  'discord',
  'android',
  'projects'
];

for (const item of items) {
  if (!existsSync(item)) continue;
  cpSync(item, `${out}/${item}`, { recursive: true });
}

const tags = [
  '<script src="/one-fabric-capability-estate-v52.js"></script>',
  '<script src="/one-fabric-interaction-estate-v53.js"></script>',
  '<script src="/one-fabric-public-transparency-v54.js"></script>',
  '<script src="/one-fabric-three-gate-experience-v55.js"></script>'
];
const inject = (path) => {
  let html = readFileSync(path, 'utf8');
  for (const tag of tags) {
    const src = tag.match(/src="([^"]+)/)?.[1] || '';
    if (src && !html.includes(src)) html = html.replace('</body>', `${tag}</body>`);
  }
  writeFileSync(path, html);
};

// Additional public-safe universal projection. Does not replace Gate 1 or grant private capabilities.
mkdirSync(`${out}/universal`, {recursive:true});
writeFileSync(`${out}/universal/index.html`,renderPublicUI());
// The public observatory is an illustration. Owner telemetry requires a
// separate authenticated tenant-scoped service and is never included here.
mkdirSync(`${out}/observatory`, {recursive:true});
writeFileSync(`${out}/observatory/index.html`,renderObservatoryUI());
mkdirSync(`${out}/agents`,{recursive:true});
writeFileSync(`${out}/agents/index.html`,renderAgentTheaterUI());
// Shared public-safe in-page bubble for Android web carrier and Telegram mini app.
mkdirSync(`${out}/assets`, {recursive:true});
cpSync('plugins/one-fabric-world/ui/one-fabric-bubble.js',`${out}/assets/8x8-bubble.js`);
cpSync('v50.html', `${out}/index.html`);
inject(`${out}/index.html`);
inject(`${out}/v50.html`);

console.log('8X8_USER_EDITION_STATIC_BUILD=PASS');
console.log('CANONICAL_ROOT=fabric://8x8/core');
console.log('OUTPUT_DIRECTORY=dist');
console.log('WEB_TELEGRAM_PRESALE_SAME_BUILD=true');
console.log('FULL_CAPABILITY_ESTATE_V52_INJECTED=true');
console.log('INTERACTION_ESTATE_V53_INJECTED=true');
console.log('PUBLIC_TRANSPARENCY_V54_INJECTED=true');
console.log('THREE_GATE_EXPERIENCE_V55_INJECTED=true');
console.log('UNIVERSAL_ATLAS_SOURCE_PROJECTION_DIST=true');
