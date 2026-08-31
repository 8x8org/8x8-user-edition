import { cpSync, existsSync, mkdirSync, rmSync } from 'node:fs';

const out = 'dist';
rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

const items = [
  'v50.html',
  'index.html',
  'manifest.webmanifest',
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

// Canonical public root is the V50 User Edition surface.
cpSync('v50.html', `${out}/index.html`);

console.log('8X8_USER_EDITION_STATIC_BUILD=PASS');
console.log('CANONICAL_ROOT=fabric://8x8/core');
console.log('OUTPUT_DIRECTORY=dist');
console.log('WEB_TELEGRAM_PRESALE_SAME_BUILD=true');
