# 8x8 Device Contribution Profiles

Status: **DESIGNED — NOT LIVE**

## User intent

An accepted 8x8 installation may be enrolled as an 8x8 node. After a user completes a separate, explicit node-enrollment and resource-consent flow, an eligible node may automatically schedule approved work within the selected limits.

Using the app, paying the USD 8.88 subscription, connecting a wallet, joining Telegram, opening a browser page, or installing a repository does not by itself authorize resource contribution.

## Device roles

Every accepted device receives one or more roles. Acceptance does not mean every device performs cryptocurrency mining.

| Role | Meaning |
|---|---|
| `CONTROLLER_ONLY` | Wallet, node dashboard, consent, receipts, remote-worker control |
| `FOREGROUND_COMPUTE` | Bounded work only while the app or page is active and visible |
| `BACKGROUND_COMPUTE` | Native service may run approved non-mining workloads in the background |
| `MINING_ELIGIBLE` | Hardware and platform may run an approved proof-of-work workload |
| `REMOTE_MINER` | Separately owned ASIC or mining rig controlled through 8x8 |
| `STORAGE_NODE` | Contributes an encrypted, hard-capped storage allocation |
| `VALIDATOR_ELIGIBLE` | May run approved proof-of-stake or protocol-validation software |

## Standard 25 profile

`STANDARD_25` is the intended default contribution offer, but it is **off until the user affirmatively enrolls**.

Maximum ceilings:

- CPU: 25% of schedulable capacity;
- GPU: 25% of schedulable capacity when supported;
- memory: 25% of currently available memory, never 25% of memory already required by the user;
- storage and bandwidth: separate hard limits chosen by the user;
- workload execution: only while all idle, thermal, power, network, policy, and integrity gates pass.

The scheduler must immediately reduce or pause contribution when interactive activity, heat, low battery, low storage, metered networking, foreground performance, or an emergency stop requires it.

## Enhanced 75 profile

`ENHANCED_75` is a separate high-resource enrollment. It is never inferred from the standard profile.

Maximum ceilings may reach 75% only when:

- the user explicitly selects the enhanced profile;
- the platform permits the workload;
- the device passes a sustained capacity and thermal canary;
- power and network requirements pass;
- the user can see the active state and expected effects;
- local pause and emergency stop remain available;
- the workload stays below the user's exact per-resource ceilings.

A profile ceiling is not a target that must always be consumed. The scheduler uses the minimum safe allocation required by current work.

## Platform execution matrix

| Surface | Local cryptocurrency mining | Other local compute | Background behavior |
|---|---:|---:|---|
| Apple App Store build | Prohibited | Only core, disclosed app functionality | Subject to iOS background limits |
| Google Play build | Prohibited | Bounded, disclosed app functionality | Subject to Android and Play policy |
| Telegram Mini App | Not supported | Foreground-only bounded web workload | Stops or suspends when the webview is inactive or closed |
| Ordinary browser | Not approved for hidden mining | Foreground-only bounded web workload | Background tabs may be throttled or frozen |
| Native desktop agent | Eligibility-gated | Supported through a signed local service | May run after explicit enrollment |
| CLI/repository installation | Eligibility-gated | Supported through a signed local service | May run after explicit enrollment |
| Remote ASIC or mining rig | Supported after allowlisting | Not applicable | Controlled and metered as remote hardware |

Mobile applications may manage remote mining hardware and display node activity. They must not mine cryptocurrency on the phone or tablet.

## Work routing

The 8x8 work router must classify hardware before assigning work. Candidate routes include:

- approved proof-of-work mining for hardware and assets that actually support it;
- proof-of-stake validation or delegated staking where legally and technically supported;
- AI inference, media processing, testing, indexing, research, storage verification, and other non-mining workloads;
- remote control of a separately owned ASIC or mining rig.

Ethereum Mainnet is proof-of-stake and is not a mineable target. Bitcoin proof-of-work should be assigned only to mining-capable hardware, normally ASIC-class equipment. Low-power devices should not be misrepresented as profitable BTC miners.

## Treasury and user accounting

Approved mining or workload proceeds may enter a designated 8x8 treasury settlement account only after the user has accepted:

- the treasury destination;
- gross-proceeds measurement;
- pool, network, exchange, conversion, custody, tax, and operating-cost treatment;
- ecosystem fee calculation;
- user reward calculation;
- settlement timing;
- dispute and correction process;
- withdrawal and asset-risk disclosures.

Every interval produces a resource receipt. Every treasury conversion produces a settlement receipt. Every user reward produces a separate reward event. Estimated, pending, simulated, unpriced, off-chain, and on-chain amounts must never be merged into one balance.

## Subscription separation

The USD 8.88 monthly subscription and node contribution are independent. A user may subscribe without contributing resources. Resource contribution may not be silently activated by subscription, installation, wallet creation, or accepting general terms.

## Current truth

The standard and enhanced profiles are public design contracts. No public mobile, browser, Telegram, desktop, CLI, treasury, mining, reward, or wallet deployment is proven live by this document.
