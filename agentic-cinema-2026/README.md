# CinemaProof Agent — Agentic Cinema 2026

CinemaProof Agent is a new, standalone hackathon project created for **Agentic Cinema: The Blockbuster Hackathon**. It is not a modification or extension of the pre-existing 8x8 platform.

## What it does

CinemaProof Agent helps filmmakers, screenwriters and studio crews convert a production brief into a structured agent workflow:

1. Story and script breakdown
2. Production bottleneck analysis
3. Shot-list and storyboard plan
4. Schedule and resource plan
5. Risk register
6. Final production packet

## Runtime AI

The app is designed to call **Gemini on Google Cloud** through the `@google/genai` package when `GEMINI_API_KEY` is configured. When credentials are missing, the app stays judgeable through a clearly labeled demo mode so reviewers can still inspect the product flow without any fake claim that live Gemini ran.

## Partner track

The intended partner track is **Replit**. The project is built with Replit Agent and is intended to be hosted on a Replit `replit.app` or `replit.dev` URL. If Replit account deployment is unavailable, the Devpost submission must remain draft until a Replit-hosted URL exists or the track is changed and the code is updated to use that partner at runtime.

## Local run

```bash
cd agentic-cinema-2026
npm install
GEMINI_API_KEY=your_key_here npm start
```

Then open `http://localhost:3000`.

## Environment

- `GEMINI_API_KEY` — required for live Gemini generation.
- `PORT` — optional; defaults to 3000.

## Truth boundary

- Live Gemini output is only claimed when the server reports `mode: live-gemini`.
- Demo outputs are labeled `mode: demo`.
- No OpenAI, Anthropic, Microsoft or AWS AI APIs are used.

## License

This project is published under the repository's Apache-2.0 license.