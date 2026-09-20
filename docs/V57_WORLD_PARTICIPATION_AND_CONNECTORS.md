# V57 World Participation, Social Impact and Connector Control Plane

Canonical root: `fabric://8x8/core`

## Participation surfaces

The public User Edition may expose opt-in participation for Planet Earth, accessibility/blind-user projects, research challenges, creator/community initiatives and other published 8x8 projects. Each project must declare its truth state, organizer, goals, accepted contribution types, donation/payment recipient where applicable, and receipts. A project card is not proof of an external partnership.

## External organizations

Any reference to the United Nations, IOM, NGOs, universities, companies or other external organizations must use verified wording. `PARTNERSHIP_VERIFIED` may be shown only when there is a current written agreement, public announcement, signed collaboration record or equivalent authoritative evidence. Otherwise use labels such as `RELATED_WORK`, `OUTREACH`, `COLLABORATION_TARGET`, `HISTORICAL_INTERACTION` or `UNVERIFIED_CLAIM` as appropriate.

## Donations

Donations are explicit user actions. Agents may explain projects, prepare donation intents and show verified destinations, but they may not silently transfer funds. A donation is successful only after independent payment confirmation and reconciliation. Donation receipts must be separate from subscription/membership receipts.

## Social and creator connectors

Social platforms, creator accounts, streaming channels, stores, communities and messaging platforms are capability-scoped connectors. Users authenticate each connector themselves and grant explicit scopes. Agents may draft, analyze, schedule, publish, reply, moderate or manage followers only within the granted scopes and platform rules. Connectors must expose state as `REGISTERED -> AUTHENTICATED -> GRANTED -> LEASED -> PRODUCTIVE -> VERIFIED`.

Embedded social interfaces must never imply that an iframe or webview grants agent control. Agent control requires a verified API/connector, or a paired local browser/device bridge explicitly authorized by the user.

## Global chat / streaming / games / build / create

The 8x8 World may provide global chat, live rooms, streaming, games, creation/build tools, Studio, research, files, agent collaboration and other capability surfaces. Each effect-bearing action is governed by capability grants and receipts. Public presence of a launcher does not imply productive backend integration.

## Mining / staking / trading

Research, simulation, calculators, watch-only dashboards and test environments may be exposed when available. Real staking, mining-resource allocation, live trading, signing, asset movement or on-chain execution must remain separately gated until the relevant network, wallet, permissions, legal/compliance and security evidence is verified.

## One-Fabric invariant

All of these surfaces remain projections of `fabric://8x8/core`; they do not create competing roots or isolated authority systems.
