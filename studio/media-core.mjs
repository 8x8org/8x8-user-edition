// © 8x8 User Edition: public, local-only media inspector. No upload or network access.
import {assessEightOEightAsset} from './film-808-release-gate.mjs';
export const MAX_BYTES = 256 * 1024 * 1024;
export const HASH_LIMIT = 32 * 1024 * 1024;
const TYPES = Object.freeze({
  image: {extensions: ['png', 'jpg', 'jpeg', 'gif', 'webp', 'avif'], mimes: ['image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/avif']},
  video: {extensions: ['mp4', 'webm', 'mov', 'm4v'], mimes: ['video/mp4', 'video/webm', 'video/quicktime', 'video/x-m4v']},
  audio: {extensions: ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac'], mimes: ['audio/mpeg', 'audio/wav', 'audio/x-wav', 'audio/ogg', 'audio/mp4', 'audio/x-m4a', 'audio/flac', 'audio/aac']}
});
export function classifyMedia(name, mime, size) {
  if (typeof name !== 'string' || typeof mime !== 'string' || !Number.isSafeInteger(size) || size < 1 || size > MAX_BYTES) return null;
  const ext = name.split('.').pop().toLowerCase();
  const cleanMime = mime.toLowerCase().split(';')[0].trim();
  for (const [kind, rule] of Object.entries(TYPES)) {
    if (rule.extensions.includes(ext) && rule.mimes.includes(cleanMime)) return {kind, mime:cleanMime};
  }
  return null;
}
export function safeName(name) {
  return String(name || 'media').replace(/[\u0000-\u001f\u007f\/\\]/g, '_').slice(0, 120);
}
export function receiptFields(file, classification) {
  return {schema:'8x8.user.local_media.v1', root:'fabric://8x8/core', original_name:safeName(file.name),
    mime:classification.mime, kind:classification.kind, bytes:file.size, modified_at:file.lastModified || null,
    provenance:'USER_SELECTED_LOCAL_FILE', uploaded:false, remote_analysis:false, model_analysis:false};
}
if (typeof document !== 'undefined') {
  const input = document.getElementById('mediaFile');
  const preview = document.getElementById('preview');
  const status = document.getElementById('status');
  const receipt = document.getElementById('receipt');
  const capture = document.getElementById('capture');
  let objectUrl = null;
  let currentVideo = null;
  const report = message => { status.textContent = message; };
  function clear() {
    if (currentVideo) {currentVideo.pause();currentVideo = null;}
    preview.replaceChildren();
    capture.hidden = true;
    receipt.textContent = '';
    if (objectUrl) URL.revokeObjectURL(objectUrl);
    objectUrl = null;
  }
  input.addEventListener('change', async () => {
    clear();
    const file = input.files?.[0];
    if (!file) { report('No local file selected.'); return; }
    const kind = classifyMedia(file.name, file.type, file.size);
    if (!kind) { report('Unsupported media type, empty file or file exceeds 256 MiB. No upload occurred.'); return; }
    objectUrl = URL.createObjectURL(file);
    const proof = receiptFields(file, kind);
    proof.sha256 = 'NOT_HASHED_SIZE_GATED';
    const element = document.createElement(kind.kind === 'image' ? 'img' : kind.kind);
    element.src = objectUrl;
    element.setAttribute('aria-label', 'Preview of selected local media');
    if (kind.kind !== 'image') {element.controls = true; element.preload = 'metadata'; element.playsInline = true;}
    if (kind.kind === 'video') {
      currentVideo = element;
      element.addEventListener('loadedmetadata', () => {
        if (currentVideo !== element || !element.isConnected) return;
        capture.hidden = false;
        proof.film808_asset_truth = assessEightOEightAsset({kind:'video', durationSeconds:element.duration});
        receipt.textContent = JSON.stringify(proof, null, 2);
        report('Local video metadata inspected. Duration does NOT certify a finished 8:08 film, rights, or publication permission.');
      });
    }
    element.addEventListener('error', () => report('Media decoder could not open this file. No upload occurred.'));
    preview.append(element);
    if (file.size <= HASH_LIMIT && globalThis.crypto?.subtle) {
      try {
        const buffer = await file.arrayBuffer();
        const hash = await crypto.subtle.digest('SHA-256', buffer);
        proof.sha256 = Array.from(new Uint8Array(hash), v => v.toString(16).padStart(2, '0')).join('');
      } catch { proof.sha256 = 'HASH_UNAVAILABLE'; }
    }
    if (objectUrl && element.isConnected) {
      receipt.textContent = JSON.stringify(proof, null, 2);
      report('Local preview ready. The file remains on this device; no remote model or transcription was invoked.');
    }
  });
  capture.addEventListener('click', () => {
    if (!currentVideo || currentVideo.readyState < 2 || !currentVideo.videoWidth || !currentVideo.videoHeight) {
      report('Play or seek the local video to load a frame first.'); return;
    }
    const canvas = document.createElement('canvas');
    canvas.width = currentVideo.videoWidth; canvas.height = currentVideo.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) {report('Frame extraction unavailable on this device.'); return;}
    ctx.drawImage(currentVideo, 0, 0);
    canvas.toBlob(blob => {
      if (!blob) {report('Frame extraction failed.'); return;}
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url; anchor.download = '8x8-local-frame.png'; anchor.click();
      setTimeout(() => URL.revokeObjectURL(url), 2000);
      report('Frame exported locally. This is a still image, not a complete video analysis.');
    }, 'image/png');
  });
  window.addEventListener('pagehide', clear, {once:true});
}
