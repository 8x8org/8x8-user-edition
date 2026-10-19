import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
const html=readFileSync(new URL('../agents/index.html', import.meta.url),'utf8');
test('public agent room is a user-initiated concept, not authenticated execution',()=>{
 assert.match(html,/CHARACTER DEMONSTRATION|conceptual figures and scripted lines/i);
 assert.match(html,/No live A2A/i);
 assert.match(html,/id="play"/);
 assert.match(html,/id="stop"/);
 assert.match(html,/aria-live="polite"/);
 assert.match(html,/pagehide/);
});
test('all five characters retain honest source classification',()=>{
 for(const name of ['JARVIS','HERMES','AEGIS','ANVIL','FLASHTM8_ASSISTANT']) assert.ok(html.includes(name));
 assert.ok(!html.includes('OWNER_ROOT'));
 assert.ok(!html.includes('auth_token'));
 assert.ok(!html.includes('127.0.0.1'));
});
test('no microphone, credential, network or unrestricted parent tool bridge exists',()=>{
 for(const forbidden of ['getUserMedia(', 'SpeechRecognition(', 'fetch(', 'XMLHttpRequest(', 'WebSocket(', 'postMessage(', 'localStorage.', 'sessionStorage.', 'eval(']) assert.ok(!html.includes(forbidden),forbidden);
 assert.ok(!html.includes('onload="'));
});
test('script syntax and no automatic voice playback',()=>{
 const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
 assert.ok(script);
 assert.doesNotThrow(()=>new vm.Script(script));
 assert.match(script,/byId\('play'\)\.addEventListener\('click'/);
 assert.ok(script.indexOf('speak(0,epoch)')>script.indexOf("byId('play')"));
});
