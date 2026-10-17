import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, symlinkSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { checkPublicReleaseInputs, APPROVED_PROJECT, CANONICAL_REPO } from '../scripts/verify-vercel-release-source.mjs';

const required = [
  'package.json', 'vercel.json', 'state/public-state.json',
  'v50.html', 'index.html', 'scripts/build-vercel-static.mjs',
  'plugins/one-fabric-world/server/public-mcp.mjs',
  'plugins/one-fabric-world/ui/one-fabric-bubble.js'
];
function publicFixture() {
  const root = mkdtempSync(join(tmpdir(), '8x8-admission-'));
  for (const p of required) {
    mkdirSync(dirname(join(root, p)), { recursive: true });
    let body = 'public safe';
    if (p === 'package.json') body = JSON.stringify({ name: '8x8-user-edition-quality-gates', scripts: { 'build:vercel': 'node scripts/build-vercel-static.mjs' } });
    if (p === 'vercel.json') body = JSON.stringify({ framework: null, buildCommand: 'npm run build:vercel', outputDirectory: 'dist' });
    if (p === 'state/public-state.json') body = JSON.stringify({ promotion_state:'PROTECTED_BETA',public_beta:true,credentials_included:false,wallet_material_included:false,remote_shell_enabled:false,live_trading_enabled:false });
    writeFileSync(join(root, p), body);
  }
  return root;
}
const valid = root => ({ root, projectId: APPROVED_PROJECT, repository: CANONICAL_REPO });
function fixtureTest(name, action) {
  test(name, () => {
    const root = publicFixture();
    try { action(root); }
    finally { rmSync(root, { recursive: true, force: true }); }
  });
}
fixtureTest('existing public source accepted as CI source-only', root => {
  assert.equal(checkPublicReleaseInputs(valid(root)).verdict, 'SOURCE_ADMISSION_PASS');
});
fixtureTest('another Vercel project is rejected even with identical public files', root => {
  assert.throws(() => checkPublicReleaseInputs({ ...valid(root), projectId: 'prj_wrong' }), /PROJECT_NOT_ALLOWLISTED/);
});
fixtureTest('noncanonical GitHub source is rejected', root => {
  assert.throws(() => checkPublicReleaseInputs({ ...valid(root), repository: 'horbolsi/8x8' }), /REPOSITORY_NOT_CANONICAL/);
});
fixtureTest('unlinked or wrongly linked project denied at release stage', root => {
  assert.throws(() => checkPublicReleaseInputs({ ...valid(root), strictLink: true }), /VERCEL_PROJECT_LINK_MISMATCH/);
  assert.throws(() => checkPublicReleaseInputs({ ...valid(root), strictLink: true, linkedProjectId: 'prj_wrong' }), /VERCEL_PROJECT_LINK_MISMATCH/);
  assert.equal(checkPublicReleaseInputs({ ...valid(root), strictLink: true, linkedProjectId: APPROVED_PROJECT }).verdict, 'SOURCE_ADMISSION_PASS');
});
fixtureTest('wrong Python/backend root denied despite copied public manifest', root => {
  mkdirSync(join(root,'core'));
  writeFileSync(join(root,'auth.py'),'# irrelevant fixture');
  assert.throws(() => checkPublicReleaseInputs(valid(root)), /BACKEND_SOURCE_IN_PUBLIC_ROOT/);
});
fixtureTest('wrong 636-file source structure without public manifests denied', root => {
  rmSync(join(root,'package.json'));
  assert.throws(() => checkPublicReleaseInputs(valid(root)), /MISSING_PUBLIC_SOURCE/);
});
fixtureTest('symlink public manifest rejected', root => {
  rmSync(join(root,'vercel.json'));
  symlinkSync(join(root,'package.json'),join(root,'vercel.json'));
  assert.throws(() => checkPublicReleaseInputs(valid(root)), /INVALID_SOURCE_FILE/);
});
fixtureTest('public tenant state may not claim credentials or trading', root => {
  writeFileSync(join(root,'state/public-state.json'),JSON.stringify({promotion_state:'PROTECTED_BETA',public_beta:true,credentials_included:true,wallet_material_included:false,remote_shell_enabled:false,live_trading_enabled:true}));
  assert.throws(() => checkPublicReleaseInputs(valid(root)), /PUBLIC_TENANT_BOUNDARY_MISMATCH/);
});
fixtureTest('Python Vercel build configuration is rejected', root => {
  writeFileSync(join(root,'vercel.json'),JSON.stringify({framework:'python',buildCommand:'uv pip install',outputDirectory:'dist'}));
  assert.throws(() => checkPublicReleaseInputs(valid(root)), /PUBLIC_BUILD_CONTRACT_MISMATCH/);
});
