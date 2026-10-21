import test from 'node:test';
import assert from 'node:assert/strict';
import {classifyMedia, receiptFields, safeName, MAX_BYTES} from '../studio/media-core.mjs';
test('accepts local supported images/videos/audio', () => {
  assert.equal(classifyMedia('still.png','image/png',10).kind,'image');
  assert.equal(classifyMedia('film.mp4','video/mp4',100).kind,'video');
  assert.equal(classifyMedia('voice.mp3','audio/mpeg',100).kind,'audio');
});
test('refuses active, mismatched and unsafe media types', () => {
  for (const [name,mime] of [['secret.html','text/html'],['evil.svg','image/svg+xml'],['fake.jpg','text/html'],['media.mp4','image/png'],['script.js','application/javascript']]) {
    assert.equal(classifyMedia(name,mime,100),null);
  }
});
test('refuses empty/oversized/non-integer input', () => {
  assert.equal(classifyMedia('a.png','image/png',0),null);
  assert.equal(classifyMedia('a.png','image/png',MAX_BYTES+1),null);
  assert.equal(classifyMedia('a.png','image/png',NaN),null);
});
test('receipt accurately bounds user selected media', () => {
  const r=receiptFields({name:'x.mp4',size:12,lastModified:10},{kind:'video',mime:'video/mp4'});
  assert.equal(r.root,'fabric://8x8/core');
  assert.equal(r.uploaded,false);
  assert.equal(r.model_analysis,false);
  assert.equal(r.bytes,12);
  assert.equal(r.sha256,undefined);
});
test('sanitizes names without preserving paths or controls', () => {
  assert.equal(safeName('a/b\\c\u0000.mp4'),'a_b_c_.mp4');
  assert.ok(safeName('x'.repeat(500)).length <= 120);
});
