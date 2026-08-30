# 8x8 OS User Edition 0.2.0 · V50

Release ID: `USER_EDITION_V50_0.2.0`  
Canonical root: `fabric://8x8/core`

## Public release scope

V50 advances the public User Edition from the earlier V40 carrier contract to a single searchable superpower interface for Web/PWA, Telegram Mini App, Discord and Android carrier source.

The public surface includes truth-labeled discovery for SERAPHIM/agents, voice/vision, Barehand spatial interaction, Browser, 8x8 Studio, Unreal/world/XR, streaming, global chat, Radio, TV, social connectors, TikTok Shop/social commerce, marketplace, NFT Studio, wallet/account observability, 8x8 and the eight functional asset models, 8x8Scan, mining/staking research, trading lab, games/worlds, Creator Factory, Builder, Research Supermind, Memory/Knowledge, 8x8 Mail, devices, robotics, security and public data.

## Carrier changes

- Web/PWA: `/` now targets the V50 public-safe interface.
- Telegram: `/telegram` is a Telegram WebApp-aware carrier surface.
- Discord: `/discord` is a dedicated public carrier surface; bot/application binding is separately verified.
- Android: `android-app/` adds an Android 8x8 User Edition WebView carrier and a GitHub Actions APK build.

## Security and authority boundary

The User Edition remains a public distribution projection, not a new One-Fabric authority root. It does not publish owner secrets, private topology, signing keys, raw user data or private runtime state.

No automatic wallet signing, payment movement, token minting, mainnet effect or live trading is enabled by V50. Connector writes, bot bindings and production-signed mobile distribution require their exact authenticated authority and readback receipts.

## Release acceptance

This release is promoted only with evidence labels. Source merge, Vercel deployment, Telegram binding, Discord binding and APK build/sign/install are separate receipts and must not be inferred from one another.
