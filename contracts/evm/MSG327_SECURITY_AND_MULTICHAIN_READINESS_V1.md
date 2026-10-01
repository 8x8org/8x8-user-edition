# MSG327 — Security and Multichain Readiness V1

Status: VERIFIED SOURCE REVIEW / NO CHAIN BROADCAST
Date: 2026-08-09 UTC

## Canonical asset family

Market assets: `8x8`, `Tx8`, `Ux8`, `Fx8`, `XM8`, `0x8`, `TM8`, `Mx8`, `Sx8`.

`SRP` remains a non-transferable verifiable credential and is not deployed with the fungible market family.

## Supply invariant

For each deployed market asset:

- immutable whole-token cap = 8,888,888;
- deployment decimals = 18 in MSG325;
- constructor initial mint = full cap to `OWNER_TREASURY`;
- holder burns reduce `totalSupply`;
- `MINTER_ROLE` may mint only into headroom below the immutable ERC20 cap;
- therefore `totalSupply <= cap` must hold for every reachable state.

Cross-network expansion MUST NOT silently multiply economic supply. Before any canonical bridge or multichain production deployment, the network packet must select and prove one supply-accounting model, such as lock/mint or burn/mint, and demonstrate a global conservation invariant across canonical and represented supply. Independent full-cap deployments on multiple production networks are forbidden unless explicitly classified as separate economic universes rather than representations of one asset.

## Authority review

Current `EightX8CappedAsset.sol` uses OpenZeppelin `AccessControl` and grants `DEFAULT_ADMIN_ROLE`, `POLICY_ADMIN_ROLE`, and `MINTER_ROLE` to the deployment `policyAdmin` address. This is acceptable for the current testnet-first candidate, but it concentrates administrative authority in one address.

Before any mainnet candidate may advance, require a dedicated authority-hardening review. Evaluate `AccessControlDefaultAdminRules` or a system-level `AccessManager`, delayed/two-step admin transfer, multisig custody, emergency role-revocation procedure, and explicit least-privilege separation between policy administration and mint authority. No migration is implied by this note; it is a release gate requiring tests and compatibility evidence.

## Counterfeit-token defense packet

Every verified deployment record must bind chain ID/network, canonical contract address, deployment transaction hash/block, exact source commit/digest, compiler/dependency lock, verified runtime bytecode digest, token metadata/cap, treasury/authority addresses, explorer verification state, and a provenance-bound 8x8 receipt.

8x8Scan and public clients must treat any token missing this canonical tuple as `UNVERIFIED` rather than inferring legitimacy from symbol/name alone.

## Bridge accounting gate

No bridge is active. A bridge packet must define canonical origin, representation contracts, message/gateway trust assumptions, replay protection, chain-ID/domain separation, rate limits, pause/recovery policy, and a machine-checkable global supply equation. Bridge activation remains OWNER_REQUIRED for production.

## Current deployment truth

Ethereum Sepolia chain `11155111` remains the first executable target. `contracts/evm/MSG325_SEPOLIA_DEPLOYMENT_SPEC.json` remains `SOURCE_PINNED_NOT_BROADCAST`. No contract address, transaction hash, explorer verification receipt, owner-wallet proof, or mint receipt exists yet.

Required runtime inputs remain `OWNER_TREASURY_PUBLIC_ADDRESS`, `POLICY_ADMIN_PUBLIC_ADDRESS`, and `FUNDED_SEPOLIA_SIGNER_CONTROLLED_BY_OWNER`.

Private keys, seed phrases, signer secrets, wallet exports and credentials must never be committed to this repository or entered into the public client.

## Next exact testnet receipt

After an owner-controlled signer path exists, each Sepolia deployment receipt must prove constructor inputs, transaction success, deployed bytecode, role assignments, `cap()`, `totalSupply()`, owner-treasury balance, decimals, burn behavior, post-burn mint headroom, failed over-cap mint, policy-digest event behavior, and source/explorer verification. Only then may deployment truth advance from source-ready to verified testnet deployment.
