# V57 Device Bridge, Barehand, Termux/iSH and Live Media

Canonical root: `fabric://8x8/core`

## User-controlled local bridge

The public web/Telegram carrier must never expose a raw unauthenticated shell or filesystem to the Internet. Device control is opt-in and mediated by a local companion bridge bound to loopback or an explicitly paired local/LAN endpoint. Pairing uses a one-time challenge and a per-device capability grant.

Supported user intents include: connect Android Termux; connect Android ADB after the user performs Android's pairing step; connect iPhone/iSH through its own local shell/file bridge; mount/select the user's 8x8 OS folder; browse/read/write only inside user-granted roots; run explicitly approved terminal operations; stream approved screen/camera/mic feeds; and provide Barehand gesture events to the spatial interface.

## Filesystem boundary

Folder access is scoped to a user-selected 8x8 OS root. No whole-device filesystem access is implied. Every mutation must carry a capability grant, selected root, relative path, operation and receipt. Destructive operations require explicit user intent.

## ADB boundary

ADB is never silently enabled or paired by the website. The user initiates Android Wireless debugging / pairing. The local bridge may then store only the resulting non-secret device endpoint/identity and use the local adb client under the user's authority. Re-pairing is required when Android invalidates the pairing.

## iPhone/iSH boundary

iSH does not provide Android ADB. It is treated as a separate local shell/file endpoint with its own capabilities and filesystem sandbox. Native iOS capabilities require an iOS-native companion rather than pretending iSH has Android-level device privileges.

## Barehand

Barehand may run full-screen after explicit camera permission. Hand tracking controls spatial pointers, grab/move/scale/throw gestures and artifact handoff. Camera use is on-demand and must stop on hide, page exit, explicit stop or revoked permission. Gesture events do not bypass file, shell, payment, signing or device capability checks.

## Live media and agents

Users may independently select text chat, speech output, push-to-talk, camera, screen share and live streaming. Jarvis, Seraphim and FlashTM8 can share the same authenticated conversation/session and selected model provider. Outbound speech does not require keeping microphone/camera open. Live streaming requires an explicit start action and visible active-state control.

## Credential Vault and models

OpenRouter and 9Router credentials are stored encrypted in the user's 8x8 Credential Vault and are never returned to the browser after storage. Provider verification and model enumeration determine the actual available model count; `500+ models` must only be displayed after the verified provider catalog returns at least 500 models for that user's account.

## Safety invariants

`DEVICE_PAIRED != SHELL_GRANTED != FILE_ROOT_GRANTED != CAMERA_GRANTED != STREAM_GRANTED`

`CREDENTIAL_STORED != PROVIDER_VERIFIED != MODEL_AVAILABLE != AGENT_TURN_PRODUCTIVE`

`GESTURE_DETECTED != FILE_MUTATION_AUTHORIZED`

Wallet signing, native 8x8 mainnet, token/NFT minting and live trading remain separately gated.
