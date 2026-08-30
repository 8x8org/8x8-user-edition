# 8x8 OS Version

**Canonical public User Edition version:** `0.2.0 Stable · V50`

Canonical root: `fabric://8x8/core`  
Public projection: `8x8org/8x8-user-edition`  
Release ID: `USER_EDITION_V50_0.2.0`

This version is the public-safe multi-carrier projection for Web/PWA, Telegram Mini App surface, Discord surface and Android carrier source. It does not publish the private owner control plane, secrets, signing material, raw user data or private runtime state.

## Reality classification

- Public web source: `PRESENT`
- Telegram Mini App surface source: `PRESENT`
- Discord surface source: `PRESENT`
- Android app source: `PRESENT`
- Vercel production: `REQUIRES_EXACT_DEPLOYMENT_READBACK`
- Telegram bot/menu binding: `REQUIRES_AUTHENTICATED_TELEGRAM_WRITE_READBACK`
- Discord bot/application binding: `REQUIRES_AUTHENTICATED_DISCORD_WRITE_READBACK`
- Android development APK: `REQUIRES_BUILD_ARTIFACT_READBACK`
- Android production-signed APK: `REQUIRES_SIGNING_AND_ARTIFACT_READBACK`
- Whole private Fabric completion: `NOT_INFERRED`

## Truth boundary

`SOURCE_PRESENT != DEPLOYED != CARRIER_BOUND != INSTALLED != PRODUCTIVE != VERIFIED`

A visible wallet, blockchain, NFT, marketplace, mining, staking or trading capability does not imply custody, signing, mainnet, minting, payment movement or live trading. Those effects remain separately gated and receipt-bound.
