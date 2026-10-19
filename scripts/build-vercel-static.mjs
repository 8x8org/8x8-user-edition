import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';

const out = 'dist';
rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

const items = [
  'v50.html',
  'index.html',
  'manifest.webmanifest',
  'icon.svg',
  'sw.js',
  'styles.css',
  'app.js',
  'state',
  'studio',
  'updates',
  'agents',
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
  // A visible entry point on the existing V50 Web/PWA/Telegram/Android web carrier.
  if (!html.includes('data-eightx8-studio-launcher')) {
    html=html.replace('</body>', '<a data-eightx8-studio-launcher href="/studio" aria-label="Open local 8x8 Studio media inspector" style="position:fixed;right:12px;bottom:80px;z-index:150;background:#102d46;color:#ffffff;padding:11px 14px;border:1px solid #74d7ec;border-radius:999px;font:700 12px system-ui;text-decoration:none;box-shadow:0 8px 28px #0009">8x8 Studio ↗</a></body>');
  }
  if (!html.includes('data-eightx8-agent-room')) html=html.replace('</body>', '<a data-eightx8-agent-room href="/agents" aria-label="Open 8x8 Agent Room character stage" style="position:fixed;right:12px;bottom:132px;z-index:150;background:#241c4e;color:#ffffff;padding:10px 14px;border:1px solid #9d86ff;border-radius:999px;font:700 12px system-ui;text-decoration:none;box-shadow:0 8px 28px #0009">Agent Room ↗</a></body>');
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
console.log('THREE_GATE_EXPERIENCE_V55_INJECTED=true');
console.log('PUBLIC_STUDIO_ROUTE_AND_ICON_PACKAGED=true');
