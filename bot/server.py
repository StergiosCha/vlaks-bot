"""ΒΛΑΞ — ο ξεναγός του αρχείου (τρεις χαρακτήρες).

    venv/bin/python bot/server.py          → http://127.0.0.1:8788

  GET  /                 το widget (σελίδα επίδειξης)
  GET  /personas         οι τρεις ξεναγοί (id, ονόματα, χαιρετισμοί, τσιπς)
  POST /chat             {"session_id", "message", "persona"} → απάντηση + υποσημείωση + κάρτες
  POST /reset            {"session_id"}
  GET  /health
  /avatar/*              τα avatars, /widget/* τα στατικά
"""
from __future__ import annotations

import logging
import os
import re
import time
import unicodedata
import uuid
from collections import defaultdict, deque

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import config
from kb import get_kb
from llm import get_provider
from personas import DEFAULT_PERSONA, PERSONAS, build_context, persona_list
from ratelimit import Limiter, client_ip

_WORD = re.compile(r"[0-9A-Za-zΆ-ώἀ-ῼ]{5,}")


# Επαναλαμβανόμενα ορθογραφικά του μοντέλου. Ο ιστότοπος είναι σχολαστικός στην τυπογραφία·
# μια ανορθόγραφη απάντηση δεν ανήκει σε αυτόν.
_TYPOS = [
    (re.compile(r"\bΤ[σς]?έσ{1,2}ερα\b"), "Τέσσερα"), (re.compile(r"\bτ[σς]?έσ{1,2}ερα\b"), "τέσσερα"),
    (re.compile(r"\bΤέσερις\b"), "Τέσσερις"), (re.compile(r"\bτέσερις\b"), "τέσσερις"),
    (re.compile(r"\bΠροφόρικη\b"), "Προφορική"), (re.compile(r"\bπροφόρικη\b"), "προφορική"),
    (re.compile(r"\bΓρεβενα\b"), "Γρεβενά"),
    (re.compile(r"\bδεχόμεθα\b(?! παραγγελ)"), "δεχόμαστε"),
    # ακλισία, τελευταία γραμμή άμυνας. Το κεφαλαίο «Βλάκες» ΔΕΝ πειράζεται:
    # είναι ο τίτλος της σελίδας «Οι Βλάκες», η μόνη επιτρεπτή εμφάνιση.
    (re.compile(r"\bβλάκες\b"), "βλαξ"), (re.compile(r"\bβλάκας\b"), "βλαξ"),
    (re.compile(r"\bβλάκα\b"), "βλαξ"), (re.compile(r"\bβλάκων\b"), "βλαξ"),
]


def _fix_typos(text: str) -> str:
    for rx, good in _TYPOS:
        text = rx.sub(good, text)
    return text


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", (s or "").lower())


def _verify_footnote(footnote: str, context: str, events: list) -> str:
    """Μια παραπομπή που δεν στέκει στα στοιχεία είναι χειρότερη από καμία παραπομπή.

    Κρατάμε το footnote μόνο αν οι λέξεις του υπάρχουν όντως στο υλικό που δόθηκε.
    Αλλιώς το αντικαθιστούμε με τις πραγματικές πηγές του γεγονότος — ή με τίποτα.
    """
    fn = (footnote or "").strip()
    if not fn:
        return ""
    hay = _norm(context)
    words = [w for w in _WORD.findall(fn)]
    if words:
        hits = sum(1 for w in words if _norm(w) in hay)
        if hits / len(words) >= 0.6:
            return fn
    for ev in events:
        if ev.sources:
            return f"Πηγές: {ev.sources[:240]}"
    return ""

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("vlax")

app = FastAPI(title="ΒΛΑΞ — ο ξεναγός")
# Το widget θα ζει στο GitHub Pages και θα μιλάει σε αυτόν τον server από άλλο origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in os.environ.get(
        "CORS_ORIGINS", "https://stergioscha.github.io,http://localhost:4321").split(",") if o],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

_sessions: dict[str, deque] = defaultdict(lambda: deque(maxlen=config.MAX_HISTORY_TURNS * 2))
_limiter = Limiter()

AVATAR_DIR = config.ASSETS_DIR / "avatar"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/avatar", StaticFiles(directory=str(AVATAR_DIR)), name="avatar")
app.mount("/widget", StaticFiles(directory=str(config.WIDGET_DIR)), name="widget")


class ChatIn(BaseModel):
    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    message: str
    persona: str = DEFAULT_PERSONA


class ResetIn(BaseModel):
    session_id: str


def _event_card(anchor: str) -> dict | None:
    kb = get_kb()
    ev = kb.events.get(anchor)
    if not ev:
        return None
    return {
        "anchor": ev.anchor, "title": ev.title, "date": ev.date_text, "venue": ev.venue,
        "badge": ev.badge, "image": ev.image, "url": ev.url, "cancelled": ev.cancelled,
    }


def answer(session_id: str, message: str, persona: str) -> dict:
    kb = get_kb()
    provider = get_provider()
    persona = persona if persona in PERSONAS else DEFAULT_PERSONA
    # Μία κουβέντα ανά επισκέπτη, όχι ανά ξεναγό: αν αλλάξεις ξεναγό στη μέση,
    # ο επόμενος ξέρει τι ειπώθηκε (και ποιος το είπε).
    history = list(_sessions[session_id])

    t0 = time.time()
    chunks = kb.search(message, k=config.TOP_K_CHUNKS)
    events = kb.find_events(message, k=6)
    context = build_context(kb, message, chunks, events)
    result = provider.generate(context, history, message, persona)

    # Η γλώσσα βγαίνει από το ΚΕΙΜΕΝΟ που έγραψε, όχι από το πεδίο που δήλωσε.
    greek = sum(1 for ch in result["reply"] if "\u0370" <= ch <= "\u03ff" or "\u1f00" <= ch <= "\u1fff")
    letters = sum(1 for ch in result["reply"] if ch.isalpha())
    result["language"] = "el" if letters and greek / letters > 0.3 else "en"

    result["reply"] = _fix_typos(result["reply"])
    result["footnote"] = _fix_typos(_verify_footnote(result["footnote"], context, events))

    cards = [c for c in (_event_card(a) for a in result["events"]) if c]
    page = kb.pages.get(result["page"]) if result["page"] in kb.pages else None
    page_out = {"slug": page.slug, "title": page.title, "url": page.url} if page else None

    _sessions[session_id].append({"role": "user", "content": message})
    _sessions[session_id].append({
        "role": "assistant",
        "content": f"({PERSONAS[persona]['name']}) {result['reply']}",
    })

    log.info("[%s] %.1fs cards=%d page=%s handoff=%s", persona, time.time() - t0, len(cards),
             page_out["slug"] if page_out else "-", result["handoff"])
    return {
        "session_id": session_id, "persona": persona,
        "reply": result["reply"], "footnote": result["footnote"], "language": result["language"],
        "events": cards, "page": page_out, "quick_replies": result["quick_replies"],
        "handoff": result["handoff"],
        "contact": {"gaps_url": kb.pages["κενα"].url if "κενα" in kb.pages else config.SITE_BASE_URL,
                    "booking_url": kb.pages["κρατησεις"].url if "κρατησεις" in kb.pages else config.SITE_BASE_URL},
        "provider": provider.name,
    }


def _throttled(reason: str, persona: str) -> JSONResponse:
    kb = get_kb()
    if reason == "daily":
        reply = ("Ο ξεναγός σχόλασε για σήμερα — έπιασε το ημερήσιο όριό του. Το αρχείο όμως "
                 "είναι ανοιχτό όλη μέρα, πέρνα μόνος σου από το χρονολόγιο.")
    else:
        reply = ("Σιγά, με πνίγεις. Πάρε ανάσα ένα λεπτό και ξαναρώτα — "
                 "στο μεταξύ το χρονολόγιο δεν πάει πουθενά.")
    return JSONResponse({
        "session_id": "", "persona": persona, "reply": reply,
        "footnote": "Όριο ρυθμού του ξεναγού. Δεν είναι κενό του αρχείου.",
        "language": "el", "events": [], "page": None,
        "quick_replies": ["Χρονολόγιο", "Αφίσες", "Το διήγημα"], "handoff": False,
        "contact": {"gaps_url": kb.pages["κενα"].url if "κενα" in kb.pages else config.SITE_BASE_URL,
                    "booking_url": config.SITE_BASE_URL},
        "throttled": reason,
    }, status_code=429)


@app.post("/chat")
def chat(body: ChatIn, request: Request):
    msg = (body.message or "").strip()
    if not msg:
        return JSONResponse({"error": "empty message"}, status_code=400)
    ip = client_ip(request)
    ok, reason = _limiter.check(ip)
    if not ok:
        log.info("throttled %s (%s)", ip, reason)
        return _throttled(reason, body.persona)
    try:
        with _limiter.slot():
            return answer(body.session_id, msg[:2000], body.persona)
    except Exception as e:  # noqa: BLE001
        log.exception("chat failed")
        _limiter.refund(ip)   # δικό μας το λάθος, δεν το χρεώνουμε στον επισκέπτη
        kb = get_kb()
        return JSONResponse({
            "session_id": body.session_id, "persona": body.persona,
            "reply": "Κάτι έσπασε στο αρχείο. Ξαναρώτα σε λίγο — ή δες μόνος σου το χρονολόγιο.",
            "footnote": "Τεχνικό σφάλμα του ξεναγού, όχι κενό του αρχείου.",
            "language": "el", "events": [], "page": None,
            "quick_replies": ["Χρονολόγιο", "Το διήγημα", "Αφίσες"],
            "handoff": False,
            "contact": {"gaps_url": kb.pages["κενα"].url if "κενα" in kb.pages else config.SITE_BASE_URL,
                        "booking_url": config.SITE_BASE_URL},
            "error": type(e).__name__,
        }, status_code=200)


@app.post("/reset")
def reset(body: ResetIn):
    _sessions.pop(body.session_id, None)
    return {"ok": True}


@app.get("/personas")
def personas_endpoint():
    return {"personas": persona_list(), "default": DEFAULT_PERSONA}


@app.get("/health")
def health():
    kb = get_kb()
    return {"ok": True, "provider": config.LLM_PROVIDER, "pages": len(kb.pages),
            "events": len(kb.events), "chunks": len(kb.chunks), "personas": list(PERSONAS),
            "limits": _limiter.stats()}


@app.get("/")
def index():
    return FileResponse(str(config.WIDGET_DIR / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=config.BOT_HOST, port=config.BOT_PORT, reload=False)
