# Canonical 8x8 Asset System

Status: **DESIGN RESOLVED — NOT ISSUED**

## Canonical count

The 8x8 economic design contains:

- **eight transferable utility-token identities**;
- **one future native 8x8 settlement coin**;
- **one non-transferable Seraphim Reputation Proof credential**, which is not counted as a market token.

This resolves the prior nine-symbol conflict without deleting Seraphim or inventing a ninth liquid market.

## Canonical utility tokens

| Symbol | Working role | Primary utility boundary |
|---|---|---|
| `Tx8` | Transaction and marketplace utility | approved market actions, transaction incentives, merchant and exchange integration |
| `Ux8` | User utility and access | product access, usage credits, subscription-related benefits, user participation |
| `Fx8` | Fabric operations | network coordination, ecosystem operations, approved treasury and service programs |
| `XM8` | Execution and compute | AI, compute, automation, inference, testing, and execution workload accounting |
| `0x8` | Protocol and innovation | developer programs, protocol upgrades, research, standards, and ecosystem building |
| `TM8` | Community and identity | community participation, loyalty, governance eligibility, creator and ambassador programs |
| `Mx8` | Mining and resource contribution | approved mining, compute, energy-aware resource contribution, and node incentives |
| `Sx8` | Storage and services | storage, availability, bandwidth, service delivery, and infrastructure incentives |

The roles are designed to reduce overlap. An implementation must not silently use one token for another token's purpose merely because both symbols contain an eight, a surprisingly weak substitute for accounting.

## 8x8 coin

The future `8x8` coin is the settlement and network-security asset for a possible 8x8 chain. Its intended functions may include:

- protocol fees;
- validator staking and slashing;
- treasury settlement;
- cross-module accounting;
- governance security deposits;
- final reward settlement;
- bridge and checkpoint security.

A distinct native coin requires a distinct ledger or chain. Bitcoin itself has BTC as its native asset. Therefore the technically coherent design is:

1. an 8x8-native coin on a future 8x8 chain;
2. Bitcoin proof-of-work checkpoint anchoring for external timestamp and finality evidence;
3. an optional Bitcoin-ecosystem representation only after selecting and auditing an exact asset protocol;
4. wrapped or bridged representations on other approved networks with one canonical supply policy.

No independent uncoordinated supply may be created on each network.

## Multinetwork policy

Target networks currently include:

- Bitcoin ecosystem;
- Ethereum and compatible networks;
- BNB Chain;
- Solana;
- TON;
- Pi Network, subject to actual technical and policy support;
- later approved networks.

Every representation must reference:

- canonical asset ID;
- canonical supply and decimals;
- origin chain or issuance authority;
- contract or asset identifier;
- bridge or mint/burn controller;
- circulating supply proof;
- audit and deployment receipt;
- pause and incident policy;
- supported wallet adapters;
- market and jurisdiction state.

A token with the same symbol on two chains is not automatically the same asset.

## Seraphim Reputation Proof

`SRP` is redefined as **Seraphim Reputation Proof**.

SRP is:

- non-transferable;
- non-saleable;
- non-swappable;
- revocable;
- expiring or periodically renewed;
- bound to a registered Seraphim identity or approved guardian instance;
- issued only from verified evidence;
- usable for security reputation, proof-review eligibility, guardian quorum participation, incident response, and trust scoring.

SRP is not:

- a ninth fungible utility token;
- an investment;
- a transferable NFT;
- a fixed-value reward;
- proof that an agent is infallible;
- permission to approve its own authority expansion.

A future SRP implementation should use a verifiable credential or equivalent non-transferable attestation. Public presentations should disclose only the minimum required claims.

## Supply and economics gate

No transferable asset receives a final supply, allocation, vesting, chain, contract, bridge, market, or launch date until the following pass:

- utility overlap review;
- legal and tax review;
- sanctions and jurisdiction controls;
- security and smart-contract audit;
- treasury and custody design;
- governance and upgrade policy;
- market manipulation and insider policy;
- bridge and cross-chain risk review;
- public risk disclosures;
- independent economic simulations;
- exact owner issuance approval;
- signed deployment receipts.

## Fee policy

The current design targets remain:

- 8x8 coin buy fee: 4.88%;
- 8x8 coin sell fee: 4.88%;
- 8x8 NFT and 8x8 Vault NFT secondary-market ecosystem fee: 4.88%;
- ordinary protocol transfer fee target: 0%, excluding unavoidable network, provider, bridge, marketplace, tax, and custody charges.

Token-specific fees require separate decisions. The 4.88% target must not be copied automatically onto every token and every transfer.

## Current truth

The identities and roles are now design-resolved. No coin, token, SRP credential, bridge, wallet representation, fee, market, liquidity pool, treasury transfer, staking system, NFT, or public reward is activated by this document.
