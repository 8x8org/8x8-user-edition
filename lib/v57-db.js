import pg from 'pg';
import crypto from 'crypto';

const { Pool } = pg;
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL ? { rejectUnauthorized: false } : undefined,
  max: 4,
  idleTimeoutMillis: 10000,
  connectionTimeoutMillis: 5000
});

const FREE_SECONDS = 5280;
const LOCK_HOURS = 24;

export function randomId(prefix) {
  return `${prefix}_${crypto.randomBytes(16).toString('hex')}`;
}

export function hashToken(token) {
  return crypto.createHash('sha256').update(token).digest('hex');
}

export function parseCookies(req) {
  const raw = req.headers.cookie || '';
  return Object.fromEntries(raw.split(';').map(v => v.trim()).filter(Boolean).map(v => {
    const i = v.indexOf('=');
    return i < 0 ? [v, ''] : [v.slice(0, i), decodeURIComponent(v.slice(i + 1))];
  }));
}

export async function ensureSchema() {
  if (!process.env.DATABASE_URL) throw new Error('DATABASE_URL_NOT_CONFIGURED');
  const c = await pool.connect();
  try {
    await c.query('BEGIN');
    await c.query(`CREATE TABLE IF NOT EXISTS eightx8_accounts (
      subject_id TEXT PRIMARY KEY,
      handle TEXT UNIQUE NOT NULL,
      display_name TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'ACTIVE',
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )`);
    await c.query(`CREATE TABLE IF NOT EXISTS eightx8_sessions (
      session_hash TEXT PRIMARY KEY,
      subject_id TEXT NOT NULL REFERENCES eightx8_accounts(subject_id) ON DELETE CASCADE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      expires_at TIMESTAMPTZ NOT NULL
    )`);
    await c.query(`CREATE TABLE IF NOT EXISTS eightx8_profiles (
      subject_id TEXT PRIMARY KEY REFERENCES eightx8_accounts(subject_id) ON DELETE CASCADE,
      bio TEXT NOT NULL DEFAULT '',
      public_name TEXT NOT NULL,
      updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )`);
    await c.query(`CREATE TABLE IF NOT EXISTS eightx8_mail_identities (
      subject_id TEXT PRIMARY KEY REFERENCES eightx8_accounts(subject_id) ON DELETE CASCADE,
      mail_handle TEXT UNIQUE NOT NULL,
      delivery_state TEXT NOT NULL DEFAULT 'IDENTITY_ONLY',
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )`);
    await c.query(`CREATE TABLE IF NOT EXISTS eightx8_wallets (
      subject_id TEXT PRIMARY KEY REFERENCES eightx8_accounts(subject_id) ON DELETE CASCADE,
      wallet_id TEXT UNIQUE NOT NULL,
      custody_mode TEXT NOT NULL DEFAULT 'WATCH_ONLY_NO_KEYS',
      signing_enabled BOOLEAN NOT NULL DEFAULT FALSE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )`);
    await c.query(`CREATE TABLE IF NOT EXISTS eightx8_avatar_profiles (
      subject_id TEXT PRIMARY KEY REFERENCES eightx8_accounts(subject_id) ON DELETE CASCADE,
      avatar_id TEXT UNIQUE NOT NULL,
      preset TEXT NOT NULL DEFAULT 'GENESIS_HUMANOID_V1',
      body_state JSONB NOT NULL DEFAULT '{}'::jsonb,
      updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )`);
    await c.query(`CREATE TABLE IF NOT EXISTS eightx8_agent_bindings (
      subject_id TEXT NOT NULL REFERENCES eightx8_accounts(subject_id) ON DELETE CASCADE,
      agent_key TEXT NOT NULL,
      role TEXT NOT NULL,
      state TEXT NOT NULL DEFAULT 'BOUND',
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      PRIMARY KEY(subject_id, agent_key)
    )`);
    await c.query(`CREATE TABLE IF NOT EXISTS eightx8_access_accounts (
      subject_id TEXT PRIMARY KEY REFERENCES eightx8_accounts(subject_id) ON DELETE CASCADE,
      remaining_active_seconds INTEGER NOT NULL DEFAULT 5280 CHECK (remaining_active_seconds BETWEEN 0 AND 5280),
      exhausted_at TIMESTAMPTZ,
      unlock_at TIMESTAMPTZ,
      membership_active BOOLEAN NOT NULL DEFAULT FALSE,
      membership_expires_at TIMESTAMPTZ,
      last_active_at TIMESTAMPTZ,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )`);
    await c.query(`CREATE TABLE IF NOT EXISTS eightx8_access_usage_receipts (
      id BIGSERIAL PRIMARY KEY,
      subject_id TEXT NOT NULL REFERENCES eightx8_accounts(subject_id) ON DELETE CASCADE,
      active_seconds INTEGER NOT NULL CHECK (active_seconds > 0 AND active_seconds <= 30),
      observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      carrier TEXT,
      receipt_key TEXT UNIQUE
    )`);
    await c.query(`CREATE TABLE IF NOT EXISTS eightx8_payment_intents (
      payment_id TEXT PRIMARY KEY,
      subject_id TEXT NOT NULL REFERENCES eightx8_accounts(subject_id) ON DELETE CASCADE,
      network TEXT NOT NULL,
      asset TEXT NOT NULL,
      receive_address TEXT NOT NULL,
      expected_amount NUMERIC,
      state TEXT NOT NULL DEFAULT 'PAYMENT_CREATED',
      tx_hash TEXT,
      confirmations INTEGER NOT NULL DEFAULT 0,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      seen_at TIMESTAMPTZ,
      confirmed_at TIMESTAMPTZ,
      reconciled_at TIMESTAMPTZ
    )`);
    await c.query('CREATE INDEX IF NOT EXISTS eightx8_usage_subject_time_idx ON eightx8_access_usage_receipts(subject_id, observed_at DESC)');
    await c.query('CREATE INDEX IF NOT EXISTS eightx8_payment_subject_time_idx ON eightx8_payment_intents(subject_id, created_at DESC)');
    await c.query('COMMIT');
  } catch (e) {
    await c.query('ROLLBACK');
    throw e;
  } finally {
    c.release();
  }
}

export async function requireSubject(req) {
  const token = parseCookies(req).x8sid;
  if (!token) return null;
  const h = hashToken(token);
  const r = await pool.query(`UPDATE eightx8_sessions
    SET last_seen_at=NOW()
    WHERE session_hash=$1 AND expires_at>NOW()
    RETURNING subject_id`, [h]);
  return r.rows[0]?.subject_id || null;
}

export async function getAccessState(subjectId) {
  const c = await pool.connect();
  try {
    await c.query('BEGIN');
    let r = await c.query('SELECT * FROM eightx8_access_accounts WHERE subject_id=$1 FOR UPDATE', [subjectId]);
    if (!r.rowCount) throw new Error('ACCESS_ACCOUNT_NOT_FOUND');
    let a = r.rows[0];
    const memberActive = a.membership_active && (!a.membership_expires_at || new Date(a.membership_expires_at) > new Date());
    if (!memberActive && a.remaining_active_seconds === 0 && a.unlock_at) {
      const reset = await c.query(`UPDATE eightx8_access_accounts
        SET remaining_active_seconds=$2, exhausted_at=NULL, unlock_at=NULL, updated_at=NOW()
        WHERE subject_id=$1 AND unlock_at<=NOW()
        RETURNING *`, [subjectId, FREE_SECONDS]);
      if (reset.rowCount) a = reset.rows[0];
    }
    await c.query('COMMIT');
    const activeMembership = a.membership_active && (!a.membership_expires_at || new Date(a.membership_expires_at) > new Date());
    return {
      remaining_active_seconds: a.remaining_active_seconds,
      membership_active: Boolean(activeMembership),
      locked: !activeMembership && a.remaining_active_seconds <= 0,
      unlock_at: a.unlock_at,
      state: activeMembership ? 'MEMBERSHIP_ACTIVE' : (a.remaining_active_seconds <= 0 ? 'LOCKED_FREE_QUOTA' : 'FREE_ACTIVE')
    };
  } catch (e) {
    await c.query('ROLLBACK');
    throw e;
  } finally {
    c.release();
  }
}

export async function heartbeat(subjectId, carrier='web') {
  const c = await pool.connect();
  try {
    await c.query('BEGIN');
    const r = await c.query('SELECT * FROM eightx8_access_accounts WHERE subject_id=$1 FOR UPDATE', [subjectId]);
    if (!r.rowCount) throw new Error('ACCESS_ACCOUNT_NOT_FOUND');
    let a = r.rows[0];
    const memberActive = a.membership_active && (!a.membership_expires_at || new Date(a.membership_expires_at) > new Date());
    if (memberActive) {
      await c.query('UPDATE eightx8_access_accounts SET last_active_at=NOW(),updated_at=NOW() WHERE subject_id=$1', [subjectId]);
      await c.query('COMMIT');
      return getAccessState(subjectId);
    }
    if (a.remaining_active_seconds === 0) {
      if (a.unlock_at && new Date(a.unlock_at) <= new Date()) {
        await c.query(`UPDATE eightx8_access_accounts SET remaining_active_seconds=$2,exhausted_at=NULL,unlock_at=NULL,last_active_at=NOW(),updated_at=NOW() WHERE subject_id=$1`, [subjectId, FREE_SECONDS]);
      }
      await c.query('COMMIT');
      return getAccessState(subjectId);
    }
    const previous = a.last_active_at ? new Date(a.last_active_at).getTime() : null;
    const now = Date.now();
    const elapsed = previous ? Math.max(0, Math.min(30, Math.floor((now - previous) / 1000))) : 0;
    if (elapsed > 0) {
      const remaining = Math.max(0, a.remaining_active_seconds - elapsed);
      const exhausted = remaining === 0;
      await c.query(`UPDATE eightx8_access_accounts SET remaining_active_seconds=$2,last_active_at=NOW(),exhausted_at=CASE WHEN $3 THEN NOW() ELSE exhausted_at END,unlock_at=CASE WHEN $3 THEN NOW()+INTERVAL '${LOCK_HOURS} hours' ELSE unlock_at END,updated_at=NOW() WHERE subject_id=$1`, [subjectId, remaining, exhausted]);
      await c.query('INSERT INTO eightx8_access_usage_receipts(subject_id,active_seconds,carrier,receipt_key) VALUES($1,$2,$3,$4) ON CONFLICT DO NOTHING', [subjectId, elapsed, carrier, randomId('usage')]);
    } else {
      await c.query('UPDATE eightx8_access_accounts SET last_active_at=NOW(),updated_at=NOW() WHERE subject_id=$1', [subjectId]);
    }
    await c.query('COMMIT');
    return getAccessState(subjectId);
  } catch (e) {
    await c.query('ROLLBACK');
    throw e;
  } finally {
    c.release();
  }
}

export { pool, FREE_SECONDS };
