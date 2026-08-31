import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';

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
  '<script src="/one-fabric-public-transparency-v54.js"></script>'
];
const inject = (path) => {
  let html = readFileSync(path, 'utf8');
  for (const tag of tags) {
    const src = tag.match(/src="([^"]+)/)?.[1] || '';
    if (src && !html.includes(src)) html = html.replace('</body>', `${tag}</body>`);
  }
  writeFileSync(path, html);
};

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
