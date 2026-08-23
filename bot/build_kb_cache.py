"""Εξάγει το KB σε ένα αρχείο, για να τρέχει ο ξεναγός χωρίς το `site/dist`.

Το `site/dist` είναι 225 MB και (σωστά) δεν μπαίνει στο git. Ο server όμως χρειάζεται
μόνο ό,τι διαβάσαμε από εκεί: 12 σελίδες, 19 κάρτες γεγονότων, 68 chunks — ~1 MB.

    venv/bin/python bot/build_kb_cache.py     # μετά από κάθε `npm run build` στο site/

Το `bot/kb_cache.json` μπαίνει στο git και ανεβαίνει στο Render.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb import CACHE_PATH, KnowledgeBase  # noqa: E402

kb = KnowledgeBase(use_cache=False)
payload = {
    "version": 1,
    "pages": {slug: asdict(p) for slug, p in kb.pages.items()},
    "events": {k: asdict(e) for k, e in kb.events.items()},
    "chunks": kb.chunks,
}
CACHE_PATH.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
size = CACHE_PATH.stat().st_size / 1024
print(f"[ok] {CACHE_PATH.name}: {len(kb.pages)} σελίδες, {len(kb.events)} γεγονότα, "
      f"{len(kb.chunks)} chunks — {size:.0f} KB")
