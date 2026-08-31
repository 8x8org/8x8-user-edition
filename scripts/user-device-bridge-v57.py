#!/usr/bin/env python3
import argparse, json, os, secrets, subprocess, sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

CANONICAL_ORIGINS={
    'https://8x8-user-8888.vercel.app',
    'http://127.0.0.1:8888',
    'http://localhost:8888'
}

def safe_root(path):
    p=Path(path).expanduser().resolve()
    if not p.exists() or not p.is_dir(): raise SystemExit(f'ROOT_NOT_FOUND={p}')
    return p

def resolve_under(root, rel):
    p=(root / str(rel or '.')).resolve()
    try: p.relative_to(root)
    except ValueError: raise PermissionError('PATH_OUTSIDE_GRANTED_ROOT')
    return p

def run(cmd, timeout=20):
    cp=subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    return {'code':cp.returncode,'output':cp.stdout[-12000:]}

class H(BaseHTTPRequestHandler):
    server_version='8x8UserBridge/57'
    def log_message(self, fmt, *args): pass
    def cors(self):
        origin=self.headers.get('Origin','')
        if origin in CANONICAL_ORIGINS:
            self.send_header('Access-Control-Allow-Origin',origin)
            self.send_header('Vary','Origin')
        self.send_header('Access-Control-Allow-Headers','Authorization, Content-Type')
        self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
        self.send_header('Cache-Control','no-store')
    def reply(self, code, obj):
        body=json.dumps(obj,separators=(',',':')).encode()
        self.send_response(code); self.cors(); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def auth(self):
        return self.headers.get('Authorization','') == f'Bearer {self.server.token}'
    def body(self):
        n=min(int(self.headers.get('Content-Length','0') or 0), 1024*1024)
        return json.loads(self.rfile.read(n) or b'{}')
    def do_OPTIONS(self):
        self.send_response(204); self.cors(); self.end_headers()
    def do_GET(self):
        if not self.auth(): return self.reply(401,{'error':'PAIRING_TOKEN_REQUIRED'})
        u=urlparse(self.path); q=parse_qs(u.query)
        if u.path=='/v1/health':
            return self.reply(200,{'schema':'8x8.user-bridge.v57','platform':self.server.platform,'root':str(self.server.root),'exec_enabled':self.server.allow_exec,'adb_available':bool(self.server.adb)})
        if u.path=='/v1/files':
            try: p=resolve_under(self.server.root,q.get('path',['.'])[0])
            except PermissionError as e: return self.reply(403,{'error':str(e)})
            if not p.is_dir(): return self.reply(400,{'error':'NOT_A_DIRECTORY'})
            rows=[]
            for x in sorted(p.iterdir(),key=lambda z:(not z.is_dir(),z.name.lower()))[:500]:
                rows.append({'name':x.name,'type':'dir' if x.is_dir() else 'file','size':x.stat().st_size if x.is_file() else None})
            return self.reply(200,{'path':str(p.relative_to(self.server.root)), 'entries':rows})
        if u.path=='/v1/file':
            try: p=resolve_under(self.server.root,q.get('path',[''])[0])
            except PermissionError as e: return self.reply(403,{'error':str(e)})
            if not p.is_file(): return self.reply(404,{'error':'FILE_NOT_FOUND'})
            if p.stat().st_size>2_000_000: return self.reply(413,{'error':'FILE_TOO_LARGE_FOR_TEXT_BRIDGE'})
            try: text=p.read_text(errors='strict')
            except UnicodeDecodeError: return self.reply(415,{'error':'BINARY_FILE_NOT_SUPPORTED_BY_TEXT_ENDPOINT'})
            return self.reply(200,{'path':str(p.relative_to(self.server.root)),'text':text})
        if u.path=='/v1/adb/status':
            if not self.server.adb: return self.reply(200,{'adb_available':False})
            return self.reply(200,{'adb_available':True,**run([self.server.adb,'devices','-l'])})
        return self.reply(404,{'error':'NOT_FOUND'})
    def do_POST(self):
        if not self.auth(): return self.reply(401,{'error':'PAIRING_TOKEN_REQUIRED'})
        u=urlparse(self.path)
        try: d=self.body()
        except Exception: return self.reply(400,{'error':'INVALID_JSON'})
        if u.path=='/v1/adb/connect':
            if not self.server.adb: return self.reply(503,{'error':'ADB_NOT_AVAILABLE'})
            endpoint=str(d.get('endpoint','')).strip()
            if not endpoint or len(endpoint)>120: return self.reply(400,{'error':'ENDPOINT_REQUIRED'})
            return self.reply(200,run([self.server.adb,'connect',endpoint]))
        if u.path=='/v1/terminal/exec':
            if not self.server.allow_exec: return self.reply(403,{'error':'EXEC_NOT_GRANTED_START_BRIDGE_WITH_ALLOW_EXEC'})
            command=str(d.get('command','')).strip()
            if not command or len(command)>1000: return self.reply(400,{'error':'COMMAND_REQUIRED'})
            cp=subprocess.run(command,shell=True,cwd=str(self.server.root),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
            return self.reply(200,{'code':cp.returncode,'output':cp.stdout[-12000:]})
        return self.reply(404,{'error':'NOT_FOUND'})

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',default=os.environ.get('EIGHTX8_OS_ROOT','~/storage/shared/8x8 OS'))
    ap.add_argument('--host',default='127.0.0.1')
    ap.add_argument('--port',type=int,default=18788)
    ap.add_argument('--token',default=os.environ.get('EIGHTX8_BRIDGE_TOKEN'))
    ap.add_argument('--allow-exec',action='store_true')
    a=ap.parse_args()
    root=safe_root(a.root); token=a.token or secrets.token_urlsafe(24)
    adb=next((p for p in ['/data/data/com.termux/files/usr/bin/adb','/usr/bin/adb'] if Path(p).exists()),None)
    srv=ThreadingHTTPServer((a.host,a.port),H); srv.root=root; srv.token=token; srv.allow_exec=a.allow_exec; srv.adb=adb; srv.platform='termux' if 'com.termux' in sys.executable else 'ish-or-unix'
    print('8X8_USER_DEVICE_BRIDGE_V57=READY'); print(f'BRIDGE_URL=http://{a.host}:{a.port}'); print(f'PAIRING_TOKEN={token}'); print(f'ROOT={root}'); print(f'EXEC_ENABLED={str(a.allow_exec).lower()}'); print('RAW_INTERNET_SHELL_EXPOSED=false' if a.host in ('127.0.0.1','localhost') else 'WARNING_NON_LOOPBACK_BIND=true'); sys.stdout.flush()
    srv.serve_forever()
if __name__=='__main__': main()
