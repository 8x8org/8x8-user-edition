import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { GoogleGenAI } from '@google/genai';

const app = express();
const port = Number(process.env.PORT || 3000);
const hasGemini = Boolean(process.env.GEMINI_API_KEY);
const ai = hasGemini ? new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY }) : null;

app.use(cors());
app.use(express.json({ limit: '1mb' }));
app.use(express.static('public'));

app.get('/api/health', (_req, res) => {
  res.json({
    ok: true,
    project: 'CinemaProof Agent',
    contest: 'Agentic Cinema 2026',
    ai_provider: 'Google Cloud Gemini',
    google_genai_package_imported: true,
    mode: hasGemini ? 'live-gemini' : 'demo',
    non_google_ai: false,
    partner_track: 'Replit',
    timestamp: new Date().toISOString()
  });
});

const demoPacket = (brief) => ({
  mode: 'demo',
  note: 'Demo mode: no live Gemini credential was configured for this run.',
  brief,
  stages: [
    { name: 'Story breakdown', output: 'Extract protagonist, conflict, visual motifs, settings, and emotional turns.' },
    { name: 'Bottleneck analysis', output: 'Flag cast availability, location permits, night shoots, VFX dependencies, and budget pressure.' },
    { name: 'Shot plan', output: 'Create establishing, coverage, insert, transition, and hero-shot groups with storyboard notes.' },
    { name: 'Schedule plan', output: 'Group scenes by location, lighting continuity, cast overlap, and crew load.' },
    { name: 'Risk register', output: 'Assign likelihood, impact, mitigation, and owner for each production risk.' },
    { name: 'Final packet', output: 'Produce a single production brief suitable for producers and assistant directors.' }
  ]
});

app.post('/api/run', async (req, res) => {
  const brief = String(req.body?.brief || '').trim();
  if (!brief) return res.status(400).json({ error: 'brief_required' });

  if (!ai) return res.json(demoPacket(brief));

  const prompt = `You are CinemaProof Agent, a production planning agent for filmmakers and studio crews. Use only the user brief below. Return concise JSON with keys: story_breakdown, bottlenecks, shot_plan, schedule_plan, risk_register, final_packet. Brief: ${brief}`;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt
    });
    res.json({
      mode: 'live-gemini',
      provider: 'Google Cloud Gemini via @google/genai',
      model: 'gemini-2.5-flash',
      output: response.text
    });
  } catch (error) {
    res.status(502).json({
      mode: 'gemini_error',
      error: String(error?.message || error)
    });
  }
});

app.listen(port, '0.0.0.0', () => {
  console.log(`CinemaProof Agent listening on ${port}`);
});
