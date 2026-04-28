#!/usr/bin/env bash
set -euo pipefail

if [ ! -d ".venv" ]; then
  python -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
fi

uvicorn backend.main:app --reload
