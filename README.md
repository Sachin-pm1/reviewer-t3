# AI Product Intelligence Platform

A **product-agnostic** platform for turning raw customer feedback into structured product
intelligence. Create a project, point it at any data source, click **Analyze**, and the
platform ingests the feedback, builds a RAG knowledge base, runs Claude to extract
structured insights, and exposes dashboards plus an AI copilot.

Spotify is just the first demo project — adding another product (Netflix, Slack, Notion,
Gaana…) needs **no core changes**, only different data sources.

> **Status:** Complete — full vertical slice with a production-grade Next.js frontend.
> Ingestion → Knowledge Base → Claude analysis → API → RAG copilot + SaaS dashboard.
> See [Roadmap](#roadmap) for optional connectors, export formats, and scaling add-ons.

---

## Architecture

Modular monolith, domain-oriented, async-first, fully typed and Pydantic-validated.
Three abstraction seams keep the platform extensible without touching the core:

```
                    AI Product Intelligence Platform

  Data Sources ──► Ingestion Engine ──► Knowledge Base ──► AI Analysis ──► Insights
   (connectors)    (BaseConnector)      (embeddings +       (Claude,        + Copilot
                                         Qdrant / RAG)       structured)

  ┌─────────────┐   ┌──────────────┐   ┌───────────────┐   ┌──────────────┐
  │ file_csv    │   │ normalize    │   │ chunk + embed │   │ per-review   │
  │ google_play │──►│ + de-dupe    │──►│ + vector      │──►│ ReviewInsight│──► dashboards
  │ (+ future)  │   │ pipeline     │   │ upsert        │   │ (Pydantic)   │    /insights
  └─────────────┘   └──────────────┘   └───────────────┘   └──────────────┘    /chat
        ▲                                      │                  ▲
   plugin registry                       retrieval (RAG) ─────────┘
```

1. **Ingestion Engine** — every source is a `BaseConnector` yielding uniform
   `RawDocument`s. Adding a source = one new file + `@register`. Nothing else changes.
2. **LLM provider abstraction** — `LLMProvider → AnthropicProvider → ClaudeService`.
   Every AI call goes through `ClaudeService`; the Anthropic SDK and API key live in
   exactly one module.
3. **Knowledge-base abstractions** — `EmbeddingProvider` and `VectorStore` interfaces;
   local sentence-transformers + local Qdrant now, swappable later.

Each domain follows **repository → service → routes**: repositories do data access,
services hold business logic, routes stay thin.

---

## Folder structure

```
app/
  core/            config (settings), logging (loguru + correlation ids), errors
  database/        async engine, declarative base, session dependency
  shared/          shared Pydantic schema primitives
  ingestion/       THE INGESTION ENGINE
    base.py        RawDocument + BaseConnector contracts
    registry.py    @register plugin registry
    normalize.py   text cleanup + chunking
    pipeline.py    collect → normalize → de-dupe
    connectors/    file_csv.py, google_play.py
  products/        Project + Product + Source (models/repo/service/routes/schemas)
  reviews/         persisted, normalized feedback items
  knowledge_base/  embeddings.py, vector_store.py, service.py (chunk/embed/store/retrieve)
  analysis/        provider/ (LLM abstraction + ClaudeService), schemas, service, routes
  agents/          report-generating agents (executive / PRD / roadmap) + registry
  chat/            RAG copilot (service/routes/schemas)
  reports/         generate, persist, and serve reports (model/repo/service/routes)
  jobs/            background Analyze lifecycle + status
  main.py          app factory, lifespan, middleware, router wiring
frontend/          Next.js 15 + TypeScript + Tailwind — the production dashboard
  src/
    app/           Next.js App Router (layout, globals.css, page)
    components/
      ui/          Button, Card, Badge, Input, Toast, ProgressBar
      layout/      Topbar (AI status), Sidebar (project list + create)
      dashboard/   SourcesTab, InsightsTab, ReviewsTab, CopilotTab, ReportsTab
    lib/           types.ts, api.ts (typed fetch client), hooks.ts (SWR), utils.ts
  next.config.ts   rewrites /api/* → FastAPI (no CORS in browser)
data/              sample_spotify_reviews.csv (+ runtime sqlite & qdrant, gitignored)
scripts/demo.py    end-to-end demo driver
tests/             unit + integration (offline; AI paths use a fake provider)
start.ps1          one-command launcher (API + frontend, Windows)
start.sh           one-command launcher (API + frontend, macOS/Linux)

spotify-aura-backend/   Standalone Part 4 MVP API — its own venv, own .env, own deploy.
  app/companion/        Discovery Companion — real Claude reasoning + real Spotify catalog
  app/spotify_client.py Client Credentials flow (app-only, no user login)
  app/catalog_routes.py Real per-mood-card track for the Discovery page
spotify-aura-frontend/  Standalone Part 4 MVP UI — 15 routes (onboarding, dashboard,
                        discovery, dna, chapters, insights, memories, settings, commute,
                        workout, wrapped, future, soundtrack, companion, landing)
```

---

## Setup

Requires **Python 3.12+** and **Node.js 18+**.

### 1 — Python backend

#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .            # or: pip install -r requirements.txt
```

#### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -e .            # or: pip install -r requirements.txt
```

### 2 — Next.js frontend
```bash
cd frontend
npm install
cd ..
```

### 3 — Configure
```bash
cp .env.example .env        # Windows: copy .env.example .env
```
Set `ANTHROPIC_API_KEY` in `.env` to enable the AI analysis + chat steps. Everything
else has working local defaults (SQLite, local Qdrant, local embeddings).

> The embedding model (`all-MiniLM-L6-v2`, ~80 MB) downloads on first use.

---

## Anthropic configuration

- All AI calls go through `ClaudeService`, backed by `AnthropicProvider` — the only place
  the Anthropic SDK and `ANTHROPIC_API_KEY` are referenced.
- Default model: **`claude-opus-4-8`** (`ANTHROPIC_MODEL`).
- Per-review analysis uses `messages.parse` with the `ReviewInsight` Pydantic schema, so
  every insight is schema-validated — never trusted as free-form text. Calls are
  concurrency-bounded (`ANALYSIS_CONCURRENCY`) and retry transient failures with backoff.
- Without a key: ingestion + knowledge-base build still work; the analyze job records a
  skip note, and `/chat` returns a clear `503 feature_unavailable`.

---

## Run

### One command (recommended)

**Windows (PowerShell):**
```powershell
.\start.ps1
```

**macOS / Linux:**
```bash
chmod +x start.sh && ./start.sh
```

Both commands start the API and the Next.js dashboard simultaneously.

| URL | Purpose |
|-----|---------|
| **http://localhost:3000** | Next.js SaaS dashboard (recommended) |
| http://localhost:8000/docs | Interactive FastAPI docs |

The Part 4 MVP (Discovery Companion + the rest of the Spotify Aura experience) is a
separate project — see "Spotify Aura MVP (Part 4)" below to run it.

### Or start servers individually

```bash
# Terminal 1 — FastAPI backend
uvicorn app.main:app --reload

# Terminal 2 — Next.js frontend
cd frontend && npm run dev
```

### End-to-end demo
With the server running:
```bash
python scripts/demo.py
```
This creates a "Spotify" project, adds the sample CSV, runs the analyze lifecycle, prints
the insights dashboard, and asks the copilot a question.

### Manual flow (curl)
```bash
# 1. Create a project
curl -X POST localhost:8000/projects \
  -H 'content-type: application/json' \
  -d '{"name":"Spotify","product_name":"Spotify"}'

# 2. Add a CSV source (use the id from step 1)
curl -X POST localhost:8000/projects/<PROJECT_ID>/sources \
  -H 'content-type: application/json' \
  -d '{"source_type":"file_csv","config":{"path":"data/sample_spotify_reviews.csv","text_column":"text","rating_column":"rating","id_column":"id"}}'

#   …or a Google Play source (no credentials needed)
#   {"source_type":"google_play","config":{"app_id":"com.spotify.music","count":200}}

# 3. Analyze (returns a job id)
curl -X POST localhost:8000/projects/<PROJECT_ID>/analyze -H 'content-type: application/json' -d '{}'

# 4. Poll the job
curl localhost:8000/jobs/<JOB_ID>

# 5. Insights dashboard
curl localhost:8000/projects/<PROJECT_ID>/insights

# 6. Ask the copilot
curl -X POST localhost:8000/projects/<PROJECT_ID>/chat \
  -H 'content-type: application/json' -d '{"question":"Why are users unhappy?"}'
```

### API summary
| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/health` | Liveness + whether AI is enabled |
| `GET`  | `/source-types` | Installed connector types |
| `POST` | `/projects` | Create a project (+ default product) |
| `GET`  | `/projects` · `/projects/{id}` | List / fetch projects |
| `POST` | `/projects/{id}/sources` | Add a data source (validated eagerly) |
| `POST` | `/projects/{id}/analyze` | Start the ingest → KB → analyze job |
| `GET`  | `/jobs/{id}` | Job status + progress |
| `GET`  | `/projects/{id}/reviews` | Browse ingested feedback |
| `GET`  | `/projects/{id}/insights` | Pain points, personas, opportunities, topics, sentiment |
| `POST` | `/projects/{id}/chat` | RAG copilot answer + citations |
| `GET`  | `/report-types` | Available report types (`executive`, `prd`, `roadmap`) |
| `POST` | `/projects/{id}/reports` | Generate a report grounded on the insights (Markdown + JSON) |
| `GET`  | `/projects/{id}/reports` · `/reports/{id}` | List / fetch generated reports |
| `POST` | `/companion/chat` | Discovery Companion — one turn of AI music-discovery chat (Part 4 MVP, stateless) |

---

## Connecting more sources

Every source is added the same way — `POST /projects/{id}/sources` with a
`source_type` and `config` (or the **Sources** tab in the dashboard) — but two of the
brief's four named source types need setup first.

### App Store — works right now, zero setup

No credentials needed; Apple serves reviews via a public RSS/JSON feed.

```json
{"source_type": "app_store", "config": {"app_id": "324684580", "country": "us"}}
```

Find `app_id` in any App Store URL: `apps.apple.com/us/app/spotify/id324684580` → `324684580`.

### Reddit — needs a free OAuth app (~2 minutes)

Public unauthenticated `reddit.com/*.json` access now returns 403 (Reddit locked this
down after their 2023 API changes — confirmed directly against this project, not
assumed). A real, free Reddit API app is required:

1. Go to **[reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)** (log in first)
   and click **create app** / **create another app**.
2. Name it anything, choose type **script**, set the redirect URI to
   `http://localhost:8000` (unused for this flow, but required by the form).
3. Click **create app**. Copy the string under the app's name (that's the **client
   id**) and the **secret** field.
4. `pip install praw` (or `pip install -e ".[collectors-extra]"`), then add to `.env`:

   ```env
   REDDIT_CLIENT_ID=<the id you copied>
   REDDIT_CLIENT_SECRET=<the secret you copied>
   ```

5. Restart the API, then add the source:

   ```json
   {"source_type": "reddit", "config": {"query": "discover new music", "subreddit": "spotify"}}
   ```

Without credentials configured, adding a `reddit` source fails immediately with a
clear `422` explaining exactly this — not a confusing failure deep into an analyze job.

### Community forums (beyond Reddit)

Not built — there's no single generic "forum" API to target. Building a connector for
a specific forum (which one?) would follow the exact same one-file pattern as the
connectors above.

---

## Database & migrations

Local-first default is **async SQLite**; tables are created on startup. Switching to
**Postgres** is a `DATABASE_URL` change only — the ORM is backend-neutral. Alembic is
included for managed migrations on the Postgres path.

## Docker

Increment 1 needs no Docker. For the production-shaped stack (API + Postgres + Qdrant
server):
```bash
ANTHROPIC_API_KEY=sk-... docker compose up --build
```
The compose file flips the app to Postgres + a Qdrant server via env vars — no code change.

---

## Deployment

Part 4 needs a *live* URL, not just `localhost`. Frontend and backend deploy to two
different platforms; this repo already has a GitHub remote, so both can deploy straight
from it with zero local CLI setup.

### 1 — Backend → Render

1. On [Render](https://render.com), **New +** → **Blueprint**, connect this repo. Render
   reads [`render.yaml`](render.yaml) and provisions a Docker web service from the
   existing [`Dockerfile`](Dockerfile).
2. Open the new service → **Environment** and paste a real `ANTHROPIC_API_KEY` (the
   blueprint deliberately leaves it blank — never commit a real key).
3. Deploy, then note the URL, e.g. `https://ai-product-intelligence-api.onrender.com`.
4. Confirm: `curl https://<your-service>.onrender.com/health` → `"ai_enabled": true`.

Free-tier caveat: the filesystem is ephemeral (SQLite/Qdrant resets on redeploy or idle
spin-down) and the instance sleeps between requests. To persist the Reviewer engine's
projects/reviews across redeploys, upgrade the instance or point `DATABASE_URL` at a
managed Postgres — see the comments in [render.yaml](render.yaml).

### 2 — Frontend → Vercel

1. On [Vercel](https://vercel.com), **Add New → Project**, import the same repo, set
   **Root Directory** to `frontend/`. Next.js is auto-detected — no other config needed.
2. Add one env var: `NEXT_PUBLIC_API_URL` = the Render URL from step 1 (no trailing
   slash). This is what `next.config.ts` rewrites `/api/*` to.
3. Deploy.

### Post-deploy smoke test

- `<vercel-url>` loads the dashboard; creating a project and adding a source works.
- `<render-url>/docs` shows the FastAPI Swagger UI.

### Deploying the Part 4 MVP (Spotify Aura)

`spotify-aura-backend/` and `spotify-aura-frontend/` are a separate project — deploy
them the same way (Render Blueprint or Web Service for the backend, Vercel with **Root
Directory** `spotify-aura-frontend/` for the frontend), pointing the frontend's
`NEXT_PUBLIC_API_URL` at the Aura backend's Render URL, not the Reviewer platform's. The
Aura backend needs its own `ANTHROPIC_API_KEY` and `SPOTIFY_CLIENT_ID`/
`SPOTIFY_CLIENT_SECRET` — see `spotify-aura-backend/.env.example`. Smoke test: the
deployed frontend's `/companion` page returns a real, Claude-generated journey with
Spotify-resolved artwork/links (iTunes fills in a preview clip when Spotify doesn't
return one for a track).

This environment had no deploy CLI or platform account access, so the steps above are
dashboard actions to run yourself rather than something executed automatically.

---

## User research (Part 2)

**Done** — 6 real interviews conducted and synthesized. See
[`research/interview-findings.md`](research/interview-findings.md) for the real
findings (feeds Part 3 directly), or the rest of [`research/`](research/) for the kit
that produced them:

- [`segment-and-screener.md`](research/segment-and-screener.md) — the original
  target-segment hypothesis and recruitment screener (see its update banner — the
  real interviews partly revised this).
- [`discussion-guide.md`](research/discussion-guide.md) — the 45-minute interview
  script, including a live concept-test of the Discovery Companion.
- [`synthesis-template.md`](research/synthesis-template.md) — the reusable template;
  see `interview-findings.md` for the filled version.
- [`example-candidate-profiles.md`](research/example-candidate-profiles.md) — **fictional**
  recruiting reference only, not interview data.

---

## Problem definition (Part 3)

**Done** — [`docs/problem-definition.md`](docs/problem-definition.md), written from
real Part 1 evidence (858 reviews, [`docs/part1-findings.md`](docs/part1-findings.md))
and real Part 2 evidence (6 interviews, [`research/interview-findings.md`](research/interview-findings.md)).
Root cause, target segment, and business case are all grounded in specific cited
evidence from both, including where the two sources independently converge on the
same mechanism and where interviews revealed something review-mining alone missed.

---

## Why AI, not just a better recommender (Part 4)

See [`docs/why-ai-mvp.md`](docs/why-ai-mvp.md) for the full argument: why traditional
recommendation systems are structurally insufficient for this problem, what an LLM
unlocks that a ranker cannot (natural-language taste negotiation, explainable
per-pick reasoning, a live adjustable novelty control), and how that changes the
listening experience — grounded in the actual Discovery Companion code, not a generic
AI pitch.

These are unfilled templates — the interviews themselves have to happen with real
people; nothing in `research/` fabricates respondent data.

---

## Testing

```bash
pip install -e ".[dev]"     # or: pip install pytest pytest-asyncio anyio
pytest
```
Tests are **fully offline**: the AI paths use a fake `LLMProvider`, and the API smoke
test avoids the embedding download. Coverage spans connectors, the registry, the
pipeline, `ClaudeService`, the analyze + aggregation flow, and API CRUD/error behavior.

---

## Coding conventions

- Async-first, fully type-annotated, Pydantic v2 for all I/O boundaries.
- Repository → service → routes per domain; routes never contain business logic.
- No `os.environ` reads outside `core/config.py`; no Anthropic calls outside the provider.
- Structured logging via Loguru with a correlation id per request/job.
- Errors are typed (`AppError` hierarchy) and mapped to consistent JSON envelopes.

---

## Roadmap

The architecture already supports these; they slot in without core changes:

- **Connectors:** Apple App Store and Reddit are **built** (`app_store`, `reddit`) — see
  [Connecting more sources](#connecting-more-sources) below. Still open: generic website
  (Playwright), PDF/DOCX interview transcripts, GitHub Discussions, RSS.
  (`pip install ".[collectors-extra]"`)
- **Modeling:** full BERTopic/spaCy/HDBSCAN topic clustering. (`".[modeling-extra]"`)
- **Agents:** executive / PRD / roadmap generator agents are **built**
  (`app/agents/`); remaining: dedicated Persona / Opportunity / Interview-analysis agents.
- **Jobs:** swap in a real queue (Celery/Arq) — the `CollectionJob` record already
  abstracts execution.
- **Reports:** executive summary / PRD / roadmap generation is **built** (Markdown +
  structured JSON via `/projects/{id}/reports`); remaining: DOCX/PDF export.
- **Frontend:** production Next.js 15 dashboard is **built** (`frontend/`) with charts,
  live job polling, chat UI, and report Markdown preview.
- **Discovery Companion (Part 4 AI-native MVP):** **built**, as a standalone project —
  `spotify-aura-backend/` + `spotify-aura-frontend/`, not part of this platform. A
  conversational agent that deliberately recommends music beyond the listener's stated
  taste, with real-catalog grounding via Spotify (Client Credentials) + iTunes as a
  preview-clip fallback, and explainable reasoning per pick. Discovery's mood cards are
  also real (a Claude-picked, Spotify-resolved representative track per card). Dashboard/
  DNA/Wrapped/Insights/Memories remain concept UI — real personalization there needs the
  full Spotify user-login (Authorization Code) flow, not yet built.
- **Persistence:** promote aggregated pain points / personas / opportunities to tables;
  Postgres as the default via Alembic.
