#!/usr/bin/env bash
# start.sh — launch the Reviewer platform (API + dashboard) and the standalone
# Spotify Aura MVP (its own API + frontend) in one command.
# Usage (from the project root):  ./start.sh
# Requires .venv (both this repo's and spotify-aura-backend's) and Node/npm.
#
# Every launch uses a subshell ( cd dir && cmd ) so this script's own working
# directory never changes — order-independent, no relative-path surprises.

set -e
set -m  # job control: each backgrounded job gets its own process group,
        # so `kill -- -$PID` below can kill a job's whole subtree, not
        # just the subshell wrapper (which would orphan npm/uvicorn).

echo ""
echo "=== AI Product Intelligence Platform ==="

# --- Reviewer platform: FastAPI backend ---
echo "[1/4] Reviewer API       → http://localhost:8000 ..."
source .venv/bin/activate 2>/dev/null || true
uvicorn app.main:app --reload --port 8000 &
API_PID=$!

# --- Reviewer platform: Next.js dashboard ---
echo "[2/4] Reviewer dashboard → http://localhost:3000 ..."
(cd frontend && npm run dev) &
FE_PID=$!

# --- Spotify Aura MVP: FastAPI backend (its own venv, separate project) ---
echo "[3/4] Spotify Aura API   → http://localhost:8010 ..."
(cd spotify-aura-backend && .venv/bin/uvicorn app.main:app --reload --port 8010) &
AURA_API_PID=$!

# --- Spotify Aura MVP: Next.js frontend (its own project) ---
echo "[4/4] Spotify Aura UI    → http://localhost:3010 ..."
(cd spotify-aura-frontend && npm run dev -- --port 3010) &
AURA_FE_PID=$!

echo ""
echo "  Reviewer dashboard → http://localhost:3000"
echo "  Reviewer API docs  → http://localhost:8000/docs"
echo "  Spotify Aura MVP   → http://localhost:3010"
echo "  Spotify Aura docs  → http://localhost:8010/docs"
echo ""
echo "Press Ctrl+C to stop all four servers."

trap "kill -- -$API_PID -$FE_PID -$AURA_API_PID -$AURA_FE_PID 2>/dev/null; echo Stopped." EXIT INT TERM
wait
