import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';

const out = 'dist';
rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

const items = [
  'v50.html',
  'index.html',
  'manifest.webmanifest',
  'one-fabric-capability-estate-v52.js',
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

// Canonical public root remains the Three-Gate surface. V52 adds a public-safe
// whole-estate denominator without creating a second authority or interface root.
const tag = '<script src="/one-fabric-capability-estate-v52.js"></script>';
const inject = (path) => {
  let html = readFileSync(path, 'utf8');
  if (!html.includes('one-fabric-capability-estate-v52.js')) {
    html = html.replace('</body>', `${tag}</body>`);
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
