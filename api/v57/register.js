import crypto from 'crypto';
import { ensureSchema, pool, randomId, hashToken } from '../../lib/v57-db.js';

const scrypt = (password, salt) => new Promise((resolve, reject) => crypto.scrypt(password, salt, 64, (e, k) => e ? reject(e) : resolve(k)));
const cleanHandle = v => String(v || '').trim().toLowerCase().replace(/[^a-z0-9_.-]/g, '').slice(0, 32);

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'METHOD_NOT_ALLOWED' });
  try {
    await ensureSchema();
    const handle = cleanHandle(req.body?.handle);
    const displayName = String(req.body?.display_name || handle).trim().slice(0, 80);
    const password = String(req.body?.password || '');
    if (handle.length < 3 || password.length < 10) return res.status(400).json({ error: 'INVALID_REGISTRATION_INPUT' });

    const c = await pool.connect();
    const subjectId = randomId('x8id');
    const walletId = randomId('x8wallet');
    const avatarId = randomId('x8avatar');
    const session = randomId('session');
    const salt = crypto.randomBytes(16);
    const key = await scrypt(password, salt);
    const credential = `${salt.toString('base64')}:${Buffer.from(key).toString('base64')}`;
    try {
      await c.query('BEGIN');
      await c.query(`CREATE TABLE IF NOT EXISTS eightx8_login_credentials (
        subject_id TEXT PRIMARY KEY REFERENCES eightx8_accounts(subject_id) ON DELETE CASCADE,
        password_record TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )`);
      await c.query('INSERT INTO eightx8_accounts(subject_id,handle,display_name) VALUES($1,$2,$3)', [subjectId, handle, displayName]);
      await c.query('INSERT INTO eightx8_login_credentials(subject_id,password_record) VALUES($1,$2)', [subjectId, credential]);
      await c.query('INSERT INTO eightx8_profiles(subject_id,public_name) VALUES($1,$2)', [subjectId, displayName]);
      await c.query('INSERT INTO eightx8_mail_identities(subject_id,mail_handle) VALUES($1,$2)', [subjectId, `${handle}@8x8`]);
      await c.query('INSERT INTO eightx8_wallets(subject_id,wallet_id) VALUES($1,$2)', [subjectId, walletId]);
      await c.query('INSERT INTO eightx8_avatar_profiles(subject_id,avatar_id) VALUES($1,$2)', [subjectId, avatarId]);
      for (const [agent, role] of [['SERAPHIM','guardian'],['FLASHTM8','owner-companion'],['JARVIS','assistant']]) {
        await c.query('INSERT INTO eightx8_agent_bindings(subject_id,agent_key,role) VALUES($1,$2,$3) ON CONFLICT DO NOTHING', [subjectId, agent, role]);
      }
      await c.query('INSERT INTO eightx8_access_accounts(subject_id) VALUES($1)', [subjectId]);
      await c.query(`INSERT INTO eightx8_sessions(session_hash,subject_id,expires_at) VALUES($1,$2,NOW()+INTERVAL '30 days')`, [hashToken(session), subjectId]);
      await c.query('COMMIT');
    } catch (e) {
      await c.query('ROLLBACK');
      if (e?.code === '23505') return res.status(409).json({ error: 'HANDLE_ALREADY_EXISTS' });
      throw e;
    } finally { c.release(); }

    res.setHeader('Set-Cookie', `x8sid=${encodeURIComponent(session)}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=2592000`);
    return res.status(201).json({
      schema: '8x8.registration.v57', canonical_root: 'fabric://8x8/core', subject_id: subjectId,
      handle, profile: { public_name: displayName },
      mail: { address: `${handle}@8x8`, state: 'IDENTITY_ONLY' },
      wallet: { wallet_id: walletId, custody_mode: 'WATCH_ONLY_NO_KEYS', signing_enabled: false },
      avatar: { avatar_id: avatarId, preset: 'GENESIS_HUMANOID_V1' },
      agents: ['SERAPHIM','FLASHTM8','JARVIS'], remaining_active_seconds: 5280,
      truth: 'ACCOUNT_CREATED_SERVER_SIDE'
    });
  } catch (e) {
    return res.status(503).json({ error: 'REGISTRATION_AUTHORITY_UNAVAILABLE', detail: String(e?.message || e) });
  }
}
