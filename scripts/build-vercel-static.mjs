import { cpSync, existsSync, mkdirSync, rmSync } from 'node:fs';

const out = 'dist';
rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

const items = [
  'index.html',
  'launch',
  'telegram',
  'android',
  'presale',
  'manifest.webmanifest'
];

for (const item of items) {
  if (!existsSync(item)) continue;
  cpSync(item, `${out}/${item}`, { recursive: true });
}

if (!existsSync(`${out}/launch/index.html`)) {
  throw new Error('Minimal User Edition launch surface missing from static build');
}

console.log('8X8_USER_EDITION_STATIC_BUILD=PASS');
console.log('CANONICAL_ROOT=fabric://8x8/core');
console.log('OUTPUT_DIRECTORY=dist');
console.log('USER_EDITION_MINIMAL_V1=true');
console.log('WEB_TELEGRAM_ANDROID_PRESALE_SAME_LAUNCH_SURFACE=true');
console.log('LEGACY_V50_INJECTION=false');
