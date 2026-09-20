import crypto from 'crypto';
import { pool } from './v57-db.js';

function masterKey() {
  const raw = process.env.EIGHTX8_VAULT_MASTER_KEY || '';
  if (!raw) throw new Error('VAULT_MASTER_KEY_NOT_CONFIGURED');
  return crypto.createHash('sha256').update(raw).digest();
}

function encryptJson(value) {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', masterKey(), iv);
  const body = Buffer.concat([cipher.update(JSON.stringify(value), 'utf8'), cipher.final()]);
  const tag = cipher.getAuthTag();
  return `${iv.toString('base64')}.${tag.toString('base64')}.${body.toString('base64')}`;
}

function decryptJson(blob) {
  const [ivB64, tagB64, bodyB64] = String(blob).split('.');
  if (!ivB64 || !tagB64 || !bodyB64) throw new Error('VAULT_BLOB_INVALID');
  const decipher = crypto.createDecipheriv('aes-256-gcm', masterKey(), Buffer.from(ivB64, 'base64'));
  decipher.setAuthTag(Buffer.from(tagB64, 'base64'));
  const plain = Buffer.concat([decipher.update(Buffer.from(bodyB64, 'base64')), decipher.final()]);
  return JSON.parse(plain.toString('utf8'));
}

export async function ensureVaultSchema() {
  await pool.query(`CREATE TABLE IF NOT EXISTS eightx8_credential_vault (
    subject_id TEXT NOT NULL REFERENCES eightx8_accounts(subject_id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    ciphertext TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'STORED_UNVERIFIED',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(subject_id, provider)
  )`);
}

export async function putCredential(subjectId, provider, secretPayload) {
  await ensureVaultSchema();
  const ciphertext = encryptJson(secretPayload);
  await pool.query(`INSERT INTO eightx8_credential_vault(subject_id,provider,ciphertext,status)
    VALUES($1,$2,$3,'STORED_UNVERIFIED')
    ON CONFLICT(subject_id,provider) DO UPDATE SET ciphertext=EXCLUDED.ciphertext,status='STORED_UNVERIFIED',updated_at=NOW()`,
    [subjectId, provider, ciphertext]);
}

export async function getCredential(subjectId, provider) {
  await ensureVaultSchema();
  const r = await pool.query('SELECT ciphertext,status FROM eightx8_credential_vault WHERE subject_id=$1 AND provider=$2', [subjectId, provider]);
  if (!r.rowCount) return null;
  return { payload: decryptJson(r.rows[0].ciphertext), status: r.rows[0].status };
}

export async function setCredentialStatus(subjectId, provider, status) {
  await pool.query('UPDATE eightx8_credential_vault SET status=$3,updated_at=NOW() WHERE subject_id=$1 AND provider=$2', [subjectId, provider, status]);
}

export async function listCredentialStatus(subjectId) {
  await ensureVaultSchema();
  const r = await pool.query('SELECT provider,status,updated_at FROM eightx8_credential_vault WHERE subject_id=$1 ORDER BY provider', [subjectId]);
  return r.rows;
}
