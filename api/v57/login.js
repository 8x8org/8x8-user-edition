import crypto from 'crypto';
import { ensureSchema, pool, randomId, hashToken } from '../../lib/v57-db.js';

const scrypt = (password, salt) => new Promise((resolve, reject) => crypto.scrypt(password, salt, 64, (e, k) => e ? reject(e) : resolve(k)));
const cleanHandle = v => String(v || '').trim().toLowerCase().replace(/[^a-z0-9_.-]/g, '').slice(0, 32);

export default async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  if(req.method!=='POST') return res.status(405).json({error:'METHOD_NOT_ALLOWED'});
  try{
    await ensureSchema();
    const handle=cleanHandle(req.body?.handle); const password=String(req.body?.password||'');
    if(!handle||!password) return res.status(400).json({error:'HANDLE_AND_PASSWORD_REQUIRED'});
    const r=await pool.query(`SELECT a.subject_id,a.display_name,c.password_record FROM eightx8_accounts a JOIN eightx8_login_credentials c USING(subject_id) WHERE a.handle=$1`,[handle]);
    if(!r.rowCount) return res.status(401).json({error:'INVALID_CREDENTIALS'});
    const [saltB64,keyB64]=String(r.rows[0].password_record).split(':');
    const got=Buffer.from(await scrypt(password,Buffer.from(saltB64,'base64')));
    const expected=Buffer.from(keyB64,'base64');
    if(got.length!==expected.length||!crypto.timingSafeEqual(got,expected)) return res.status(401).json({error:'INVALID_CREDENTIALS'});
    const session=randomId('session');
    await pool.query(`INSERT INTO eightx8_sessions(session_hash,subject_id,expires_at) VALUES($1,$2,NOW()+INTERVAL '30 days')`,[hashToken(session),r.rows[0].subject_id]);
    res.setHeader('Set-Cookie',`x8sid=${encodeURIComponent(session)}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=2592000`);
    return res.status(200).json({schema:'8x8.login.v57',subject_id:r.rows[0].subject_id,display_name:r.rows[0].display_name,state:'AUTHENTICATED'});
  }catch(e){return res.status(503).json({error:'LOGIN_AUTHORITY_UNAVAILABLE',detail:String(e?.message||e)})}
}
