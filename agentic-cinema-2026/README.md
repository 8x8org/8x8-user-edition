# CinemaProof — Production Twin + Evidence Graph

**Agentic Cinema 2026 competition-window project**

CinemaProof is a new standalone media-production agent created during the contest period. It is branded as a capability from the ©️8x8 by FlashTM8 ⚡️🌎🤖 research lineage, but it does **not** claim that the pre-existing 8x8 platform was created for this hackathon.

## The problem

Film crews pay for decisions after they become expensive: continuity mistakes, location changes, schedule collisions, impractical VFX, unsafe ideas, late talent, and factual assumptions that survive until shoot day.

CinemaProof moves those failures left.

## Core idea

CinemaProof compiles a production brief into a **Production Digital Twin**:

`SCRIPT → SCENES → CONTINUITY → LOCATIONS → SHOTS → CREW → SCHEDULE → RISKS → EVIDENCE`

Then a director can change a decision and see which downstream production assumptions become invalid before the crew commits.

Every recommendation is represented as a proof edge:

`SOURCE → CONSTRAINT → LIVE EVIDENCE → DECISION → CONFIDENCE → OVERRIDE → DOWNSTREAM EFFECT`

## Runtime integrations

### Parallel Search MCP — PRESENT_PROVEN

The deployed competition surface actively calls Parallel's official Search MCP at runtime through:

`https://search.parallel.ai/mcp`

The app performs the MCP initialize handshake and invokes the `web_search` tool. A public read-only runtime probe has returned live Parallel results and source URLs. This is not a README-only integration.

### Gemini — CODE_PRESENT / LIVE_RUNTIME_GATED

The agent uses the official `@google/genai` SDK and is designed to return `mode=live-gemini` only when `GEMINI_API_KEY` is configured. If it is not configured, CinemaProof falls back to a clearly labeled demo packet and does not represent demo output as live model output.

### Google Cloud Agent Builder — REQUIRED BEFORE FINAL SUBMISSION

The hackathon requires Gemini **and Google Cloud Agent Builder**. Final submission must not claim this gate is complete until the live Google Cloud Agent Builder path is activated and verified.

## Public deployment

- Judge surface: https://8x8-os-ecosystem.vercel.app/cinemaproof
- Telegram Mini App carrier: https://8x8-os-ecosystem.vercel.app/telegram/cinemaproof
- Parallel runtime probe: https://8x8-os-ecosystem.vercel.app/api/cinemaproof-grounding?probe=1

The Telegram publication workflow verifies the bot identity, sets the Mini App menu, reads the menu back, and fails closed on mismatch.

## Run locally

Requires Node.js 20+.

```bash
cd agentic-cinema-2026
npm install
npm run dev
```

For live Gemini generation:

```bash
export GEMINI_API_KEY="YOUR_KEY"
npm run dev
```

Never commit provider credentials.

## Judge path

1. Open the hosted CinemaProof surface.
2. Click **Ground Live Evidence**.
3. Verify the UI reports **LIVE PARALLEL** and inspect returned source URLs.
4. Select a director override.
5. Compile the production proof.
6. Verify the runtime label: **LIVE GEMINI** only when a real Gemini call succeeded; otherwise **DEMO MODE**.
7. Inspect the scene graph, risk topology, override blast radius, shot plan, schedule, continuity plan and proof packet.

## Truth boundary

- Pre-existing ©️8x8 work is preserved as prior work, not contest-period implementation.
- No funded token sale, wallet signing, token minting, mainnet action, or financial effect is part of CinemaProof.
- Demo content is labeled.
- Safety information is decision support, not a legal or professional safety certification.
- External prize rank is determined by judges and is never self-certified.

## License

CinemaProof is licensed under Apache License 2.0. See [LICENSE](./LICENSE).
