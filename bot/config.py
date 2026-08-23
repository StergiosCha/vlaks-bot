"""Config for the ΒΛΑΞ bot (three personas, Gemini/Claude, archive-backed).

Env (bot/.env):
  LLM_PROVIDER      gemini | claude            (default gemini)
  GEMINI_API_KEY    (+ _2 … _10, or a .api_key file) — bpan-style rotation
  GEMINI_MODELS     comma-separated priority list (optional)
  ANTHROPIC_API_KEY / CLAUDE_MODEL / CLAUDE_EFFORT
  SITE_BASE_URL     default https://stergioscha.github.io/vlaks
  BOT_HOST / BOT_PORT
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BOT_DIR = Path(__file__).resolve().parent
REPO_DIR = BOT_DIR.parent
load_dotenv(REPO_DIR / ".env")
load_dotenv(BOT_DIR / ".env", override=True)   # bot/.env wins over shell env

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini").strip().lower()

ARCHIVE_DIR = REPO_DIR / "archive"
TEXTS_DIR = REPO_DIR / "texts"
NORMALIZED_DIR = REPO_DIR / "normalized"
SITE_DIR = REPO_DIR / "site"
ASSETS_DIR = BOT_DIR / "assets"
WIDGET_DIR = BOT_DIR / "widget"

SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "https://stergioscha.github.io/vlaks").rstrip("/")

# --- Gemini (same wiring as bpan_app / the Kouts shop bot) ---
_env_models = os.environ.get("GEMINI_MODELS", "").strip()
GEMINI_MODELS = (
    [m.strip() for m in _env_models.split(",") if m.strip()]
    if _env_models
    else ["gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-flash-latest"]
)
GEMINI_TIMEOUT = int(os.environ.get("GEMINI_TIMEOUT", "60"))
GEMINI_VERTEX = os.environ.get("GEMINI_VERTEX", "0") == "1"

# --- Claude ---
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5")
CLAUDE_EFFORT = os.environ.get("CLAUDE_EFFORT", "low")
CLAUDE_MAX_TOKENS = int(os.environ.get("CLAUDE_MAX_TOKENS", "2048"))

TOP_K_CHUNKS = int(os.environ.get("TOP_K_CHUNKS", "7"))
MAX_HISTORY_TURNS = int(os.environ.get("MAX_HISTORY_TURNS", "8"))

BOT_HOST = os.environ.get("BOT_HOST", "127.0.0.1")
BOT_PORT = int(os.environ.get("BOT_PORT", "8788"))


def gemini_keys() -> list[str]:
    keys: list[str] = []
    for i in range(1, 11):
        name = "GEMINI_API_KEY" if i == 1 else f"GEMINI_API_KEY_{i}"
        val = (os.environ.get(name) or "").strip()
        if val and val not in keys:
            keys.append(val)
    if not keys:
        for p in (BOT_DIR / ".api_key", REPO_DIR / ".api_key"):
            if p.exists():
                v = p.read_text().strip()
                if v:
                    keys.append(v)
                    break
    return keys
