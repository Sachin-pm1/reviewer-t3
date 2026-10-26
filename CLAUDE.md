# AI Product Intelligence Platform — Claude Context

## What this project is

A **product-agnostic AI Product Intelligence Platform**. NOT a Spotify analyzer — Spotify is just the first demo. Adding another product (Netflix, Slack, Gaana, Notion) requires NO core changes, only different data sources.

The platform: create a Project → add data sources → click Analyze → ingests feedback, builds a RAG knowledge base, runs Claude to extract structured insights → exposes a SaaS dashboard + AI copilot + report generator.

---

## Build status — everything below is DONE and VERIFIED. Do not re-implement.

### Backend (FastAPI + Python 3.13)
- Ingestion Engine: `BaseConnector` plugin registry — `file_csv`, `google_play`, `app_store` (no credentials), `reddit` (needs `REDDIT_CLIENT_ID`/`SECRET`) connectors
- Knowledge Base: sentence-transformers embeddings + local Qdrant vector store
- Analysis: `ClaudeService` → `AnthropicProvider` → per-review `ReviewInsight` via `messages.parse`
- Agents: `executive`, `prd`, `roadmap` report agents
- Chat: RAG copilot with source citations
- Jobs: `CollectionJob` background job with live progress polling
- CORS: `CORSMiddleware` wired in `app/main.py`, origins via `CORS_ORIGINS` env var
- Tests: 27 tests, all passing, fully offline (fake LLMProvider)

> The `app/web/static/` fallback vanilla UI described in earlier versions of this file was removed in the "Aura" commit (`main.py` was cleaned up to match — no dangling `/ui` mount). There is no fallback UI anymore; use the Next.js frontend.

### Frontend (Next.js 15.3.3 + TypeScript + Tailwind)
- Location: `frontend/`
- Production build: **verified passing** (exit 0)
- `/api/*` rewrites to FastAPI backend via `next.config.ts` — no CORS issues
- Views: Sources (add + analyze + live job progress), Insights (KPI cards + sentiment pie + topic bar + pain points + personas + opportunities), Reviews, Copilot (chat UI + citations), Reports (generate + history + Markdown preview + download)
- The `/aura/*` concept-UI tree that used to live here was removed — it moved to and was rebuilt as the standalone `spotify-aura-frontend/` project (see below). This frontend is now exclusively the "reviewer" data-collection + analysis platform.

### Launch scripts
- `start.ps1` — Windows one-command: starts API (:8000) + Next.js (:3000)
- `start.sh` — macOS/Linux equivalent

---

## Spotify Aura — the Part 4 MVP (separate deployable project)

**Not part of the platform above.** `spotify-aura-backend/` + `spotify-aura-frontend/` are a
standalone, independently deployable app — the case-study's Part 4 AI-native MVP. They
have their own dependencies, their own `.env`, and are not imported by (or importing
from) `app/` or `frontend/`. Original 14-page Aura concept UI + Companion logic was
ported from this repo's git history (`git show HEAD:frontend/src/app/aura/...`) when the
old `/aura/*` tree was removed.

- `spotify-aura-backend/` (FastAPI, its own venv) — real Claude reasoning (`app/claude.py`,
  same `messages.parse` pattern as the main platform) + real Spotify catalog access via
  the **Client Credentials flow** (`app/spotify_client.py` — app-only auth, no user login,
  catalog search only, never touches anyone's personal listening data) + iTunes as a
  `preview_url` fallback when Spotify doesn't return one (`app/companion/catalog.py`).
  Routes: `POST /companion/chat` (the AI Companion), `POST /catalog/experience-track`
  (real, Claude-picked + Spotify-resolved representative track per Discovery/Commute/
  Workout/Soundtrack mood card, in-memory cached by card title). Has its own accounts
  system (below) — separate from and unrelated to Spotify login itself.
- **Accounts** (`app/auth/`) — real signup/signin, not tied to Spotify: bcrypt password
  hashing, JWT sessions (`JWT_SECRET` in `.env` — auto-generates a per-process random one
  if unset, logging a warning; every restart then signs everyone out, so set a real value
  before deploying), `GET`/`PUT /me/taste` persists the taste profile per-account (falls
  back to browser localStorage when signed out). `POST /auth/signup`, `POST /auth/signin`,
  `GET /auth/me`. Stricter separate rate limit on the two auth routes
  (`AUTH_RATE_LIMIT_PER_MINUTE`, default 10/min) than the general per-IP budget.
- **Real Spotify user login** (`app/spotify_connect/`) — the Authorization Code flow (real
  user consent, distinct from the app-only Client Credentials flow above). One app-account
  user links one real Spotify account: `GET /auth/spotify/login` (authenticated, returns an
  `authorize_url`) → full-page redirect to Spotify → `GET /auth/spotify/callback` (exchanges
  the code, stores tokens **encrypted at rest** via Fernet/`TOKEN_ENCRYPTION_KEY`, redirects
  back to `/settings?spotify=connected|error`) → `GET /me/spotify/status`,
  `GET /me/spotify/overview` (bundled profile + top artists/tracks + recently played + a
  genre tally, auto-refreshing the access token via the stored refresh token when expired),
  `POST /me/spotify/disconnect`. CSRF/account-linking across the redirect uses a one-time,
  short-TTL in-memory `state` token (`app/spotify_connect/service.py`), same pattern as the
  experience-track cache. Scopes: `user-read-email user-read-private user-top-read
  user-read-recently-played` — deliberately no playback-control or library-write scopes.
  Unless the Spotify app has extended quota, every Spotify account that signs in must be
  added under the app's Dashboard → User Management (up to 25).
- `spotify-aura-frontend/` (Next.js, its own project) — 17 routes: `/` (landing) →
  `/onboarding` → `/dashboard` + full sidebar nav to discovery, dna, chapters, insights,
  memories, settings, commute, workout, wrapped, future, soundtrack, companion, plus
  `/signin` and `/signup`. **Genuinely real** (backed by the API calls above, not mock
  data): Onboarding (self-reported taste, no API needed), Companion (real AI reasoning +
  real catalog grounding + per-account taste profile when signed in), Discovery/Commute/
  Workout/Soundtrack (real Spotify/iTunes-resolved representative track per mood card),
  Settings (real Connect/Disconnect Spotify flow + real profile card), sign up / sign in.
  **Partially real once Spotify is connected** (Settings → Connect Spotify): Dashboard
  (real greeting + real top track), Music DNA (real top genres/artists section, additive
  to the illustrative radar), Insights (real top-genre badges + real genre count KPI),
  Memories (real recently-played tracks grouped by their actual date, replacing the
  fabricated diary days), Wrapped (real top-artist/top-track/top-genre slides inserted
  alongside the illustrative ones) — each page clearly labels what's still illustrative
  and shows a "Connect Spotify" banner when not connected, rather than silently faking data.
  **Deliberately still 100% illustrative**: Life Chapters — Spotify's API exposes no
  multi-year historical listening log, so there is no honest way to back a "life story"
  view with real data regardless of the OAuth scope granted; the page says so directly.
- Run: `cd spotify-aura-backend && .venv/bin/uvicorn app.main:app --port 8010`, and
  separately `cd spotify-aura-frontend && npm run dev -- --port 3010`. Needs its own
  `ANTHROPIC_API_KEY` and `SPOTIFY_CLIENT_ID`/`SPOTIFY_CLIENT_SECRET` in
  `spotify-aura-backend/.env` (Spotify app must be Web API only; Client Credentials
  requires the registering Spotify account to be Premium, the Authorization Code flow
  above additionally requires `SPOTIFY_REDIRECT_URI` to exactly match a Redirect URI
  registered on the app, plus every signing-in Spotify account added under Dashboard →
  User Management unless extended quota was granted — see `.env.example` in that dir).
- Tests: `cd spotify-aura-backend && .venv/bin/pip install -e ".[dev]" && .venv/bin/python -m pytest -q`
  — 46 tests, fully offline (fake Claude, monkeypatched Spotify/iTunes/OAuth seams), same
  "isolated env, no real credentials" pattern as the main platform's tests/conftest.py.

---

## How to run

```powershell
# Windows — one command
.\start.ps1
```
```bash
# macOS/Linux
./start.sh
```

Or separately:
```bash
# Terminal 1
uvicorn app.main:app --reload

# Terminal 2
cd frontend && npm run dev
```

- Dashboard: http://localhost:3000
- API docs: http://localhost:8000/docs
- Spotify Aura MVP (separate project, run separately — see below): http://localhost:3010, API at :8010

---

## Setup (fresh machine)

```powershell
# Python backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .

# Frontend
cd frontend
npm install
cd ..

# Config
copy .env.example .env   # then set ANTHROPIC_API_KEY
```

---

## Architecture — three abstraction seams (never break these)

### 1. Ingestion Engine
`app/ingestion/base.py` — `RawDocument` + `BaseConnector` ABC.
Adding a new source = one file in `app/ingestion/connectors/` + `@register`. Nothing else changes.

### 2. LLM Provider
`LLMProvider` → `AnthropicProvider` → `ClaudeService`.
**`import anthropic` only in `app/analysis/provider/anthropic_provider.py`.**
**`ANTHROPIC_API_KEY` only read in `app/core/config.py`.**
Every AI call routes through `ClaudeService` in `app/analysis/provider/claude_service.py`.

### 3. Knowledge Base
`EmbeddingProvider` + `VectorStore` interfaces. Concrete: sentence-transformers + local Qdrant. Swappable via env var, no code change.

### Domain pattern (always follow)
`repository → service → routes` per domain. Routes never contain business logic.

---

## Key files

```
app/
  core/config.py                   Settings — only place reading env vars
  core/errors.py                   AppError hierarchy
  database/base.py                 async engine + Base + init_models()
  database/session.py              get_session() + session_scope()
  ingestion/base.py                RawDocument + BaseConnector
  ingestion/registry.py            @register, available_source_types(), build_connector()
  ingestion/normalize.py           normalize_text, chunk_text(max_chars=1000, overlap=150)
  ingestion/pipeline.py            async def ingest()
  ingestion/connectors/file_csv.py      source_type="file_csv"
  ingestion/connectors/google_play.py   source_type="google_play"
  ingestion/connectors/app_store.py     source_type="app_store" — no credentials needed
  ingestion/connectors/reddit.py        source_type="reddit" — needs REDDIT_CLIENT_ID/SECRET
  products/                        Project + Product + Source domain
  reviews/                         Review model + routes
  knowledge_base/                  embeddings.py, vector_store.py, service.py
  analysis/provider/anthropic_provider.py   ONLY anthropic SDK import
  analysis/provider/claude_service.py       ClaudeService gateway
  analysis/schemas.py              ReviewInsight + InsightsOverview
  analysis/service.py              AnalysisService (Semaphore-bounded concurrency)
  agents/                          ReportAgent ABC + executive/prd/roadmap agents
  chat/                            RAG copilot
  jobs/                            CollectionJob + run_analyze_job() orchestrator
  reports/                         ReportService + routes
  main.py                          App factory — all routers + CORS
  models_registry.py               Imports ALL ORM models (required by init_models)

frontend/
  src/lib/types.ts                 TypeScript mirrors of all Pydantic response schemas
  src/lib/api.ts                   Typed fetch client (/api/* prefix)
  src/lib/hooks.ts                 SWR hooks per resource
  src/lib/utils.ts                 cn(), SOURCE_TEMPLATES, formatDate, sentimentColor
  src/components/ui/               Button, Card, Badge, Input, Toast, ProgressBar
  src/components/layout/           Topbar, Sidebar
  src/components/dashboard/        SourcesTab, InsightsTab, ReviewsTab, CopilotTab, ReportsTab
  src/app/page.tsx                 Root page — selectedProjectId state
  next.config.ts                   /api/* → FastAPI rewrite

spotify-aura-backend/              Standalone — see "Spotify Aura" section above
  app/config.py                    Its own Settings — separate .env, separate secrets
  app/claude.py                    ONLY anthropic SDK import in this project
  app/spotify_client.py            Client Credentials token + search (app-only, no user login)
  app/companion/                   schemas.py, catalog.py (Spotify + iTunes-fallback enrichment), service.py, routes.py
  app/catalog_routes.py            POST /catalog/experience-track — real track per mood card
  app/spotify_connect/             Real user login (Authorization Code): models.py (SpotifyConnection,
                                    encrypted tokens), crypto.py (Fernet), client.py (exchange/refresh/
                                    /v1/me/* calls), service.py (pending-state store + overview assembly),
                                    routes.py (/auth/spotify/login,callback + /me/spotify/status,overview,disconnect)
  app/main.py                      App factory

spotify-aura-frontend/             Standalone — see "Spotify Aura" section above
  src/app/layout-shell.tsx          Sidebar nav shared by all 15 routes
  src/app/page.tsx                  Landing — redirects signed-in users away, has its own Sign in/up buttons
  src/app/onboarding/, dashboard/, discovery/, dna/, chapters/, insights/,
    memories/, settings/, commute/, workout/, wrapped/, future/, soundtrack/,
    companion/                      One route each — see per-page "real vs concept" notes above
  src/lib/api.ts                    companion.chat(), catalog.experienceTrack(), spotifyConnect.{login,status,overview,disconnect}()
  next.config.ts                    /api/* → its own FastAPI backend (:8010 by default)
```

---

## Tech stack (authoritative)

| Concern | Choice |
|---------|--------|
| Claude model | `claude-opus-4-8` (NO date suffix) |
| Anthropic client | `anthropic.AsyncAnthropic()` |
| Structured output | `client.messages.parse(output_format=ReviewInsight)` |
| DB default | SQLite + aiosqlite (`DATABASE_URL` env to switch to Postgres) |
| Vector store | Qdrant local mode (`QDRANT_URL` env to switch to server) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (~80 MB, downloads on first use) |
| Frontend | Next.js 15.3.3, React 19, Tailwind 3, SWR, Recharts, react-markdown |
| Tests | pytest + pytest-asyncio, asyncio_mode=auto, fully offline |

---

## Environment variables (see .env.example for full docs)

```
ANTHROPIC_API_KEY=          # required for AI features only
ANTHROPIC_MODEL=claude-opus-4-8
ANALYSIS_CONCURRENCY=5
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
QDRANT_PATH=./data/qdrant
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
REDDIT_CLIENT_ID=                 # only needed for the reddit connector
REDDIT_CLIENT_SECRET=             # only needed for the reddit connector
```

---

## REST API surface

| Method | Path | Notes |
|--------|------|-------|
| GET | `/health` | `{status, ai_enabled, model}` |
| GET | `/source-types` | Registered connector types |
| GET | `/report-types` | `["executive","prd","roadmap"]` |
| POST | `/projects` | `{name, product_name, description?}` → ProjectDetail |
| GET | `/projects` / `/projects/{id}` | List / detail |
| POST | `/projects/{id}/sources` | `{source_type, config}` → SourceRead |
| POST | `/projects/{id}/analyze` | `{max_reviews_per_source?}` → JobRead (202) |
| GET | `/jobs/{id}` | Poll progress |
| GET | `/projects/{id}/reviews` | `?limit=50` |
| GET | `/projects/{id}/insights` | InsightsOverview (run analyze first) |
| POST | `/projects/{id}/chat` | `{question, top_k?}` → ChatResponse |
| GET | `/projects/{id}/chat` | Past copilot exchanges, oldest first → ChatHistoryItem[] |
| POST | `/projects/{id}/reports` | `{report_type}` → ReportRead |
| GET | `/projects/{id}/reports` / `/reports/{id}` | List / detail |

Error envelope: `{"error": {"code": "...", "message": "..."}}`

---

## What is NOT yet built (optional roadmap — no core changes needed)

- **More connectors:** `app_store` and `reddit` are built (see Key files above — Reddit needs `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET`, see README "Connecting more sources"). Still open: Playwright, PDF/DOCX, RSS, GitHub Discussions — add one file + `@register`
- **Report export:** DOCX/PDF — add `render_docx()` to each agent
- **More agents:** Persona agent, Opportunity agent — same pattern as executive/prd/roadmap
- **Job queue:** Celery/Arq — swap `BackgroundTasks` in `app/jobs/routes.py`; `CollectionJob` row unchanged
- **Postgres default:** set `DATABASE_URL=postgresql+asyncpg://...` + run Alembic
- **Spotify Aura — Life Chapters real data:** unlike Dashboard/DNA/Insights/Memories/Wrapped (now partially real via `app/spotify_connect/`, see above), Life Chapters has no honest path to real data — Spotify's API exposes no multi-year historical listening log at any OAuth scope. Would need years of the user's own logged listening data from an external source.

---

## Non-negotiable rules

1. Never add `import anthropic` outside `app/analysis/provider/anthropic_provider.py`
2. Never read `os.environ` or `ANTHROPIC_API_KEY` outside `app/core/config.py`
3. Every new data source = new connector file only. Never touch the pipeline/service/analysis layers.
4. Routes stay thin — no business logic in route handlers.
5. All new features must be production-quality (user's explicit requirement: "no compromise").
