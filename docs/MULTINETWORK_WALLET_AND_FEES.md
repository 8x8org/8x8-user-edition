# 8x8 Multinetwork Wallet and Fee Boundary

Status: **DESIGNED — NOT LIVE**

## Product goal

A future 8x8 wallet may present one user interface across multiple networks while preserving separate chain accounts, signing domains, transaction fees, asset contracts, confirmations, risks, and receipts.

The intended network roadmap currently includes Bitcoin, Ethereum-compatible networks, BNB Chain, Solana, TON, Pi Network, and later approved networks. A network label in a roadmap does not prove that an asset, bridge, market, wallet adapter, or deployment exists on that network.

## Custody boundary

The preferred first implementation is non-custodial or user-controlled custody:

- users control their wallet keys or approved signing devices;
- 8x8 receives only the minimum public addresses and permissions needed for the requested operation;
- seed phrases and private keys never enter public repositories, analytics, contribution receipts, mining manifests, or agent memory;
- every network adapter has an independent permission and signing boundary;
- treasury accounts are separate from user accounts;
- an agent may prepare a transaction, but high-impact signing and broadcast remain separately gated.

Custodial services, pooled balances, internal exchange functions, asset conversion, or user withdrawals require additional licensing, safeguarding, accounting, sanctions, tax, and consumer-protection gates.

## Asset inventory blocker

The stated goal is **eight utility tokens plus one 8x8 coin**. Prior project records currently contain nine utility-token symbols in addition to 8x8:

- `Tx8`
- `Ux8`
- `Fx8`
- `XM8`
- `0x8`
- `TM8`
- `SRP`
- `Mx8`
- `Sx8`

No issuance package may proceed until one canonical asset registry resolves which eight utility tokens are in scope, whether one symbol is a module rather than a token, and which network hosts each canonical asset.

## Draft fee policy

The current owner-directed design target is:

- 8x8 coin buy fee: 4.88%;
- 8x8 coin sell fee: 4.88%;
- 8x8 NFT and 8x8 Vault NFT secondary buy/sell ecosystem fee: 4.88%;
- ordinary wallet transfer protocol fee target: 0%, excluding unavoidable network, validator, bridge, exchange, marketplace, custody, tax, or payment-provider charges.

These are design targets, not live charges. Every quote must separate:

1. asset amount;
2. network fee;
3. bridge or conversion fee;
4. marketplace or exchange fee;
5. 8x8 ecosystem fee;
6. taxes or legally required deductions;
7. final amount received.

The interface must not describe a 4.88% fee as the only cost when other costs apply.

## Treasury flow

A future settlement may route approved proceeds to an 8x8 treasury account. The accounting system must distinguish:

- gross mined or workload proceeds;
- pool fees;
- network and validator fees;
- conversion and exchange costs;
- operating costs;
- 8x8 ecosystem fee;
- user reward pool;
- treasury reserve;
- pending disputes;
- finalized user entitlement;
- paid or on-chain-settled reward.

No agent may convert, transfer, stake, bridge, trade, or distribute treasury assets without exact policy, budget, custody, jurisdiction, and high-impact authorization gates.

## Subscription boundary

The USD 8.88 monthly subscription remains separate from wallet balances, token purchases, NFT purchases, mining enrollment, and node contribution. The subscription must not automatically purchase an asset, enroll a device, or authorize treasury settlement.

## Trading and swapping

A future wallet may expose approved swap or trade routes only through regulated or otherwise legally available providers for the user's jurisdiction. “Tradable,” “sellable,” and “buyable” are deployment outcomes that require actual liquidity, provider support, contracts, markets, disclosures, and receipts. They are not guaranteed by creating a token contract or displaying a button.

## Current truth

No 8x8 coin, eight-token canonical set, multinetwork wallet, bridge, exchange, swap route, 4.88% live fee, treasury settlement, NFT fee, or public trading market is proven live by this document.
