// ©️8x8 by FlashTM8 — local, no-network 8:08 film asset truth gate.
// This gate classifies selected media; it never approves or publishes media.
export const EIGHT_O_EIGHT_SECONDS = 8 * 60 + 8;
export const DURATION_TOLERANCE_SECONDS = 0.5;

export function assessEightOEightAsset({ kind, durationSeconds } = {}) {
  const measurable = kind === 'video' && Number.isFinite(durationSeconds) && durationSeconds > 0;
  const observedSeconds = measurable ? Math.round(durationSeconds * 1000) / 1000 : null;
  const fullLength = measurable && Math.abs(durationSeconds - EIGHT_O_EIGHT_SECONDS) <= DURATION_TOLERANCE_SECONDS;
  const assetClass = !measurable ? 'DURATION_UNVERIFIED' : fullLength ? 'EIGHT_O_EIGHT_DURATION_MATCH' : 'NOT_FULL_EIGHT_O_EIGHT';
  return {
    schema: '8x8.studio.eight_oh_eight_asset_truth.v1',
    root: 'fabric://8x8/core',
    asset_class: assetClass,
    observed_duration_seconds: observedSeconds,
    intended_episode_seconds: EIGHT_O_EIGHT_SECONDS,
    duration_measured_locally: measurable,
    full_episode_duration_match: fullLength,
    release_state: 'FUTURE_GATED',
    publicly_publishable: false,
    unverified_requirements: [
      'COMPLETE_MOTION_AND_AUDIO_QC',
      'RIGHTS_AND_LIKENESS_CLEARANCE',
      'OWNER_APPROVAL_AND_STOP_GATE',
      'PROVIDER_SCOPED_AUTHENTICATION',
      'SIGNED_PUBLICATION_AND_DEDUPLICATION_RECEIPT'
    ],
    explanation: 'Duration alone is never proof of finished film, media rights or publication approval.'
  };
}
