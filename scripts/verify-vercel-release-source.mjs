// 8x8 User Edition: source admission for the supported, owner-approved Vercel release path.
// This does not grant Vercel credentials or prevent a privileged user from bypassing this script.
import { existsSync, lstatSync, readFileSync, realpathSync } from 'node:fs';
import { resolve } from 'node:path';
import { execFileSync, spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

export const CANONICAL_REPO = '8x8org/8x8-user-edition';
export const APPROVED_PROJECT = 'prj_ouaSkH3EADTdaQ8enpFlEd4D0vUU';

function reject(reason) {
  throw new Error('8X8_RELEASE_ADMISSION_DENIED: ' + reason);
}
function regularFile(root, pathname) {
  const path = resolve(root, pathname);
  if (!path.startsWith(root + '/') || !existsSync(path)) reject('MISSING_PUBLIC_SOURCE:' + pathname);
  if (!lstatSync(path).isFile() || lstatSync(path).isSymbolicLink()) reject('INVALID_SOURCE_FILE:' + pathname);
  return path;
}
function loadJSON(root, pathname) {
  try { return JSON.parse(readFileSync(regularFile(root, pathname), 'utf8')); }
  catch (error) {
    if (String(error.message).startsWith('8X8_RELEASE_ADMISSION_DENIED:')) throw error;
    reject('INVALID_PUBLIC_JSON:' + pathname);
  }
}
export function checkPublicReleaseInputs({ root, projectId, repository, linkedProjectId, strictLink = false }) {
  const base = realpathSync(resolve(root));
  if (projectId !== APPROVED_PROJECT) reject('PROJECT_NOT_ALLOWLISTED');
  if (repository !== CANONICAL_REPO) reject('REPOSITORY_NOT_CANONICAL');
  const required = [
    'package.json', 'vercel.json', 'state/public-state.json',
    'v50.html', 'index.html', 'scripts/build-vercel-static.mjs',
    'plugins/one-fabric-world/server/public-mcp.mjs',
    'plugins/one-fabric-world/ui/one-fabric-bubble.js'
  ];
  for (const pathname of required) regularFile(base, pathname);
  const forbidden = ['core', 'agents', 'auth.py', 'background_loop.py'];
  for (const pathname of forbidden) if (existsSync(resolve(base, pathname))) reject('BACKEND_SOURCE_IN_PUBLIC_ROOT');
  const pkg = loadJSON(base, 'package.json');
  const vercel = loadJSON(base, 'vercel.json');
  const state = loadJSON(base, 'state/public-state.json');
  if (pkg.name !== '8x8-user-edition-quality-gates' ||
      pkg.scripts?.['build:vercel'] !== 'node scripts/build-vercel-static.mjs' ||
      vercel.buildCommand !== 'npm run build:vercel' ||
      vercel.outputDirectory !== 'dist' ||
      vercel.framework !== null) reject('PUBLIC_BUILD_CONTRACT_MISMATCH');
  if (state.promotion_state !== 'PROTECTED_BETA' || state.public_beta !== true ||
      state.credentials_included !== false ||
      state.wallet_material_included !== false ||
      state.remote_shell_enabled !== false ||
      state.live_trading_enabled !== false) reject('PUBLIC_TENANT_BOUNDARY_MISMATCH');
  if (strictLink && linkedProjectId !== APPROVED_PROJECT) reject('VERCEL_PROJECT_LINK_MISMATCH');
  return Object.freeze({ verdict: 'SOURCE_ADMISSION_PASS', repository: CANONICAL_REPO, projectId });
}
function normalizeRemote(remote) {
  return String(remote || '').trim().replace(/\.git$/, '')
    .replace(/^git@github\.com:/, '').replace(/^ssh:\/\/git@github\.com\//, '')
    .replace(/^https:\/\/github\.com\//, '');
}
function git(root, ...args) {
  try { return execFileSync('git', args, { cwd: root, encoding: 'utf8', stdio: ['ignore','pipe','ignore'] }).trim(); }
  catch { reject('GIT_ORIGIN_OR_ROOT_UNVERIFIED'); }
}
export function inspectCurrentRelease({ root = process.cwd(), projectId, sourceOnly = false }) {
  const base = realpathSync(resolve(root));
  if (realpathSync(git(base, 'rev-parse', '--show-toplevel')) !== base) reject('NOT_GIT_ROOT');
  const origin = normalizeRemote(git(base, 'remote', 'get-url', 'origin'));
  if (origin !== CANONICAL_REPO) reject('GIT_ORIGIN_MISMATCH');
  const fromRunner = process.env.GITHUB_REPOSITORY;
  if (fromRunner && fromRunner !== CANONICAL_REPO) reject('CI_REPOSITORY_MISMATCH');
  let linkedProjectId;
  if (!sourceOnly) {
    const linked = loadJSON(base, '.vercel/project.json');
    linkedProjectId = linked.projectId;
  }
  return checkPublicReleaseInputs({
    root: base, projectId, repository: origin, strictLink: !sourceOnly, linkedProjectId
  });
}
// Only the owner's explicit preview command can invoke Vercel.
// A successful static-source check is not a production promotion approval.
export function previewOnlyRelease({ root = process.cwd(), projectId, spawn = spawnSync }) {
  const base = realpathSync(resolve(root));
  const receipt = inspectCurrentRelease({ root: base, projectId, sourceOnly: false });
  if (process.env.VERCEL_PROJECT_ID && process.env.VERCEL_PROJECT_ID !== APPROVED_PROJECT) {
    reject('ENV_PROJECT_MISMATCH');
  }
  if (git(base, 'status', '--porcelain')) reject('SOURCE_WORKTREE_NOT_CLEAN');
  const result = spawn('vercel', ['deploy', '--target=preview'], {
    cwd: base, stdio: 'inherit', env: process.env, shell: false
  });
  if (result.error) reject('VERCEL_CLI_UNAVAILABLE_OR_FAILED');
  if (result.status !== 0) reject('PREVIEW_DEPLOY_COMMAND_FAILED');
  return { ...receipt, effect: 'PREVIEW_DEPLOYMENT_COMMAND_SUCCEEDED' };
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    const args = process.argv.slice(2);
    const projectFlag = args.find(x => x.startsWith('--target-project='));
    const targets = args.filter(x => x.startsWith('--target-project='));
    const sourceOnly = args.includes('--ci-source-only');
    const deployPreview = args.includes('--deploy-preview');
    if (!projectFlag || targets.length !== 1 || (sourceOnly && deployPreview) ||
        args.some(x => !x.startsWith('--target-project=') && x !== '--ci-source-only' && x !== '--deploy-preview')) {
      reject('USAGE_TARGET_PROJECT_REQUIRED_EXACTLY_ONCE');
    }
    const projectId = projectFlag.slice('--target-project='.length);
    const receipt = deployPreview
      ? previewOnlyRelease({ projectId })
      : inspectCurrentRelease({ projectId, sourceOnly });
    console.log('8X8_RELEASE_ADMISSION=' + receipt.verdict + ' PROJECT_ALLOWLIST_CONFIRMED=true');
    console.log('8X8_RELEASE_EFFECT=' + (receipt.effect || 'NONE') + ' no_credentials_echoed=true');
  } catch (error) {
    console.error(String(error.message));
    process.exitCode = 1;
  }
}
