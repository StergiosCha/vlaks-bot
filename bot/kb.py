"""ΒΛΑΞ knowledge base — built from the *published* site (site/dist) plus the archive CSVs.

The site is the truth: it already applies overrides.ts, the redaction rules and the
confidence asterisks. We parse it, so the bot can never contradict the page a visitor
is looking at.

Produces:
  Page   — one per built page (text for retrieval, url for linking)
  Event  — one per <article class="event"> card (date, venue, poster, sources, anchor)
  chunks — BM25 corpus (page paragraphs + one chunk per event + archive texts)
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from rank_bm25 import BM25Okapi

from config import ARCHIVE_DIR, BOT_DIR, SITE_BASE_URL, SITE_DIR, TEXTS_DIR

# Το KB μπορεί να έρθει είτε από το χτισμένο site είτε από αυτό το cache (για deploy
# χωρίς τα 225 MB του site/dist — δες bot/build_kb_cache.py).
CACHE_PATH = BOT_DIR / "kb_cache.json"

_TOKEN_RE = re.compile(r"[a-z0-9Ͱ-Ͽ]+")

_SYNONYMS = {
    "βλαξ": ["vlax", "παρτι", "party"],
    "παρτι": ["party", "βλαξ", "vol"],
    "αφισα": ["poster", "αφισες"],
    "αφισες": ["poster", "αφισα"],
    "φωτο": ["φωτογραφιες", "photo", "gallery"],
    "φωτογραφια": ["φωτογραφιες", "photo"],
    "μουσικη": ["music", "τραγουδια", "σετ", "dj"],
    "τραγουδι": ["μουσικη", "music"],
    "διηγημα": ["ιστορια", "story", "κειμενο"],
    "ιστορια": ["διηγημα", "story"],
    "κρατηση": ["κρατησεις", "booking", "ντιτζειλικι", "λαιβ"],
    "κρατησεις": ["booking", "λαιβ", "προσφορα"],
    "τιμη": ["κρατησεις", "χιλιαρικα", "λαιβ"],
    "ημερομηνια": ["χρονολογιο", "date"],
    "χρονολογιο": ["timeline", "ημερομηνια", "vol"],
    "καφε": ["fuit", "cafe", "μαγαζι"],
    "μαγαζι": ["fuit", "cafe", "καφε"],
    "γρεβενα": ["grevena", "fuit"],
    "σκρολτς": ["skrolts", "ρεκορ"],
    "αδερφες": ["αδελφες", "sisters"],
    "μπατζανακης": ["ηλιθιος", "μπατιρης", "βλαξ"],
    "ντενεκες": ["μπατζανακης", "τενεκες"],
    "γιατρος": ["θεμης", "tziros", "τζιρος"],
    "τρομπονι": ["φουιτ", "χαλκινα", "brass"],
    "party": ["παρτι", "βλαξ"],
    "poster": ["αφισα", "αφισες"],
    "music": ["μουσικη"],
    "photos": ["φωτογραφιες", "φωτο"],
    "booking": ["κρατησεις"],
    "timeline": ["χρονολογιο"],
    "story": ["διηγημα"],
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.replace("ς", "σ")


_SYNONYMS = {normalize(k): v for k, v in _SYNONYMS.items()}


def tokenize(text: str, expand: bool = False) -> list[str]:
    toks = _TOKEN_RE.findall(normalize(text))
    if not expand:
        return toks
    out: list[str] = []
    for t in toks:
        out.append(t)
        out.extend(_SYNONYMS.get(t, []))
        if len(t) > 5 and t.endswith(("εσ", "ων", "ια", "ου")):
            out.append(t[:-2])
        elif len(t) > 4 and t.endswith("s"):
            out.append(t[:-1])
    return out


# Nav order + one-line purpose, from DESIGN.md §8 (kept short: it rides in every prompt).
PAGE_INFO = {
    "": ("Αρχική", "Ο μονόλιθος: wordmark, «Πάρτι 80s που έγινε σκυλάδικο. Γρεβενά, από το 2016.», επόμενο πάρτι, μαρκίζα «προς ΒΛΑΞ»."),
    "διηγημα": ("Το διήγημα", "Το κείμενο «Ο θάνατος του μπατζανάκη μου» με τις υποσημειώσεις στο περιθώριο."),
    "χρονολογιο": ("Χρονολόγιο", "Κάθε τεκμηριωμένο γεγονός: ημερομηνία, χώρος, αφίσα, «πώς το ξέρουμε». Κόκκινος αστερίσκος = συναγόμενη ημερομηνία."),
    "διαφωνιες": ("Τα στοιχεία διαφωνούν", "Όπου οι πηγές μαλώνουν (vol.04, η καρέκλα) — η διαφωνία γραμμένη, όχι κρυμμένη."),
    "αφισες": ("Αφίσες", "Ο τοίχος: οι αφίσες σε πλήρη ανάλυση, χωρίς κρop."),
    "φωτογραφιες": ("Φωτογραφίες", "Γκαλερί ανά βραδιά — φλας στις 3 τα ξημερώματα, ως έχει."),
    "μουσικη": ("Μουσική", "Τι έπαιζε: Νίνο, Καρβέλας, Βανδή, σκα/πανκ σετ, χάλκινα, ο Φούιτ στο τρομπόνι. Και η απόδειξη ότι ηχογραφήσεις ΒΛΑΞ δεν υπάρχουν."),
    "βλαξ": ("Οι Βλάκες", "Δύο στήλες: «ο ηλίθιος» / «ο μπατίρης». Ποιος είναι ποιος δεν λέγεται ποτέ."),
    "fuit": ("Fuit", "Το καφέ: Ηλία Φάσσα 2, Γρεβενά. Το μανιφέστο, τα βραβεία, ο σκαντζόχοιρος, ο χάρτης."),
    "κρατησεις": ("Κρατήσεις", "«ΔΕΝ ΔΕΧΟΜΕΘΑ ΠΑΡΑΓΓΕΛΙΕΣ» — αλλά ντι-τζέιλίκια αναλαμβάνουμε, πολύ επιλεκτικά. Οι όροι είναι γραμμένοι."),
    "κενα": ("Κενά", "Τι λείπει από το αρχείο και ζητείται: αφίσες vol.01–03, φωτογραφίες, μνήμες."),
    "en": ("English", "Chrome σε αγγλικά· το διήγημα και οι ανακοινώσεις μένουν ελληνικά."),
}


@dataclass
class Page:
    slug: str
    title: str
    url: str
    text: str


@dataclass
class Event:
    anchor: str
    page_slug: str
    title: str
    date_text: str
    date_iso: str
    venue: str
    badge: str
    announcement: str
    sources: str
    image: str | None
    cancelled: bool

    @property
    def url(self) -> str:
        base = f"{SITE_BASE_URL}/{self.page_slug}/" if self.page_slug else f"{SITE_BASE_URL}/"
        return f"{base}#{self.anchor}" if self.anchor else base


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _chunk(text: str, size: int = 1400, overlap_sentences: int = 1) -> list[str]:
    """Κόβει κείμενο σε κομμάτια που χωράνε σε prompt.

    Το κείμενο που βγάζουμε από το site ΔΕΝ έχει κενές γραμμές (το get_text ενώνει με
    κενά), οπότε το σπάσιμο σε παραγράφους από μόνο του άφηνε μια σελίδα 33.000
    χαρακτήρων να γίνεται ένα κομμάτι των 1.400 — δηλαδή πετούσε το 96% του διηγήματος.
    Γι' αυτό: πρώτα παράγραφοι αν υπάρχουν, αλλιώς προτάσεις σε παράθυρα, με μία
    πρόταση επικάλυψη ώστε να μην κόβεται νόημα στη μέση.
    """
    text = (text or "").strip()
    if not text:
        return []
    blocks = [b.strip() for b in re.split(r"\n{2,}", text) if b.strip()] or [text]
    out: list[str] = []
    for block in blocks:
        if len(block) <= size:
            out.append(block)
            continue
        sentences = [x for x in re.split(r"(?<=[.;!·…])\s+", block) if x.strip()]
        cur: list[str] = []
        n = 0
        for sent in sentences:
            while len(sent) > size:                      # μονοκόμματη τερατώδης πρόταση
                if cur:
                    out.append(" ".join(cur))
                    cur, n = [], 0
                out.append(sent[:size])
                sent = sent[size:]
            if n + len(sent) + 1 > size and cur:
                out.append(" ".join(cur))
                cur = cur[-overlap_sentences:] if overlap_sentences else []
                n = sum(len(x) + 1 for x in cur)
            cur.append(sent)
            n += len(sent) + 1
        if cur:
            out.append(" ".join(cur))
    return out


class KnowledgeBase:
    def __init__(self, use_cache: bool = True) -> None:
        self.pages: dict[str, Page] = {}
        self.events: dict[str, Event] = {}
        self.chunks: list[dict] = []
        self._bm25: BM25Okapi | None = None
        self.source = ""
        self.timeline_rows: list[dict] = []
        self.timeline_text = ""
        if use_cache and not (SITE_DIR / "dist").exists() and CACHE_PATH.exists():
            self.load_cache()
        else:
            self.load()

    # ---------- load ----------
    def load_cache(self) -> None:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        self.pages = {k: Page(**v) for k, v in data["pages"].items()}
        self.events = {k: Event(**v) for k, v in data["events"].items()}
        self.chunks = data["chunks"]
        self._bm25 = BM25Okapi([tokenize(f"{c['title']} {c['text']}", expand=True) for c in self.chunks])
        self.source = "cache"

    def load(self) -> None:
        # Το BeautifulSoup χρειάζεται ΜΟΝΟ για να διαβαστεί το χτισμένο site. Στο deploy
        # τρέχουμε από το kb_cache.json, οπότε δεν είναι runtime εξάρτηση.
        from bs4 import BeautifulSoup  # noqa: PLC0415

        self._soup = BeautifulSoup
        dist = SITE_DIR / "dist"
        if not dist.exists():
            raise RuntimeError(
                f"Δεν βρέθηκε ούτε το build του site ({dist}) ούτε το {CACHE_PATH.name}. "
                "Τρέξε `npm run build` στο site/ και μετά `python bot/build_kb_cache.py`."
            )
        self.source = "site/dist"

        for html_file in sorted(dist.rglob("index.html")):
            slug_parts = html_file.relative_to(dist).parts[:-1]
            if any(p in ("_astro", "media", "video") for p in slug_parts):
                continue
            slug = "/".join(slug_parts)
            soup = self._soup(html_file.read_text(encoding="utf-8"), "html.parser")
            # events first (and remove them from the page text so they aren't double-indexed)
            for art in soup.select("article.event"):
                ev = self._parse_event(art, slug)
                if ev:
                    self.events[ev.anchor or f"{slug}-{len(self.events)}"] = ev
                art.decompose()

            for junk in soup.select("script, style, nav, header, footer"):
                junk.decompose()
            main = soup.select_one("main") or soup.body or soup
            text = _clean(main.get_text(" ")) if main else ""
            title = PAGE_INFO.get(slug, (None, ""))[0] or _clean(soup.title.get_text() if soup.title else slug)
            url = f"{SITE_BASE_URL}/{slug}/" if slug else f"{SITE_BASE_URL}/"
            self.pages[slug] = Page(slug=slug, title=title, url=url, text=text)

        self._enrich_from_timeline()
        self._build_chunks()

    def _parse_event(self, art, slug: str) -> Event | None:
        h = art.select_one("h3")
        if not h:
            return None
        t = art.select_one("time")
        img = art.select_one("img")
        det = art.select_one("details")
        src = _clean(det.get_text(" ")) if det else ""
        src = re.sub(r"^πώς το ξέρουμε\s*", "", src)
        venue_el = art.select_one(".venue")
        badge = _clean(venue_el.select_one(".badge").get_text()) if venue_el and venue_el.select_one(".badge") else ""
        venue = _clean(venue_el.get_text(" ")) if venue_el else ""
        if badge:
            venue = _clean(venue.replace(badge, "", 1))
        image = None
        if img and img.get("src"):
            s = img["src"]
            image = s if s.startswith("http") else SITE_BASE_URL.rsplit("/vlaks", 1)[0] + s if s.startswith("/vlaks") else s
        return Event(
            anchor=art.get("id", ""),
            page_slug=slug,
            title=_clean(h.get_text()),
            date_text=_clean(t.get_text()) if t else "",
            date_iso=(t.get("datetime") if t and t.get("datetime") else ""),
            venue=venue,
            badge=badge,
            announcement=_clean(art.select_one(".ann").get_text(" ")) if art.select_one(".ann") else "",
            sources=src,
            image=image,
            cancelled="cancelled" in (art.get("class") or []),
        )

    def _enrich_from_timeline(self) -> None:
        """Προαιρετικό, μόνο για δουλειά τοπικά: γραμμές του αρχείου που το site δεν
        δείχνει ως κάρτες. Το deploy τρέχει από το cache και δεν χρειάζεται το CSV,
        γι' αυτό όλα όσα θέλει ο server ζουν μέσα στο bot/."""
        p = ARCHIVE_DIR / "timeline.csv"
        if not p.exists():
            return
        rows = list(csv.DictReader(p.open(encoding="utf-8")))
        self.timeline_rows = rows
        self.timeline_text = "\n\n".join(
            f"[{r['event_id']}] {_clean(r['event_name'])} — {r['date_iso'][:10]} ({r['weekday']}), "
            f"{r['venue']}, {r['city']} · σειρά: {r['series']} · ακρίβεια ημερομηνίας: {r['date_confidence']}\n"
            f"{_clean(r['announcement_text'])[:400]}\nΠηγή: {r['sources']}"
            for r in rows if r.get("event_name")
        )

    def _build_chunks(self) -> None:
        chunks: list[dict] = []
        for slug, page in self.pages.items():
            for i, body in enumerate(_chunk(page.text)):
                chunks.append({
                    "id": f"page-{slug or 'home'}-{i}", "type": "page", "title": page.title,
                    "url": page.url, "slug": slug, "text": body,
                })
        for key, ev in self.events.items():
            body = (
                f"Γεγονός: {ev.title}\nΗμερομηνία: {ev.date_text}\nΧώρος: {ev.venue}\n"
                + (f"Σειρά: {ev.badge}\n" if ev.badge else "")
                + (f"ΜΑΤΑΙΩΘΗΚΕ\n" if ev.cancelled else "")
                + f"Ανακοίνωση/περιγραφή: {ev.announcement}\nΠώς το ξέρουμε: {ev.sources}"
            )
            chunks.append({
                "id": f"event-{key}", "type": "event", "title": ev.title, "url": ev.url,
                "slug": ev.page_slug, "event_anchor": ev.anchor, "text": body,
            })
        # archive-only prose: conflicts, gaps, the manuscript & FB transcripts
        for f, typ, title in [
            (ARCHIVE_DIR / "conflicts.md", "archive", "Τα στοιχεία διαφωνούν (αρχείο)"),
            (ARCHIVE_DIR / "gaps.md", "archive", "Κενά (αρχείο)"),
            (TEXTS_DIR / "o-thanatos-tou-mpatzanaki-mou.md", "story", "Ο θάνατος του μπατζανάκη μου"),
            (TEXTS_DIR / "fb-posts-transcript.md", "source", "Μεταγραφές ποστ Facebook"),
            (TEXTS_DIR / "kytio-paraponon-intro.md", "source", "Κυτίο παραπόνων"),
            (TEXTS_DIR / "chantzis-posts-raw.txt", "source", "Ποστ Χαντζή (πρωτογενές)"),
        ]:
            if not f.exists():
                continue
            url = self.pages.get({"story": "διηγημα"}.get(typ, ""), self.pages.get("", None)).url if self.pages else SITE_BASE_URL
            for i, body in enumerate(_chunk(f.read_text(encoding="utf-8", errors="replace"))):
                chunks.append({"id": f"{f.stem}-{i}", "type": typ, "title": title, "url": url, "slug": "", "text": body})

        self.chunks = chunks
        self._bm25 = BM25Okapi([tokenize(f"{c['title']} {c['text']}", expand=True) for c in chunks])

    # ---------- retrieval ----------
    def search(self, query: str, k: int = 7) -> list[dict]:
        assert self._bm25 is not None
        q = tokenize(query, expand=True)
        if not q:
            return []
        scores = self._bm25.get_scores(q)
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        out = []
        for i in order[:k]:
            if scores[i] <= 0:
                break
            c = dict(self.chunks[i])
            c["score"] = round(float(scores[i]), 2)
            out.append(c)
        return out

    def find_events(self, query: str, k: int = 6) -> list[Event]:
        q = set(tokenize(query, expand=True))
        scored = []
        for ev in self.events.values():
            hay = set(tokenize(f"{ev.title} {ev.badge} {ev.venue} {ev.date_text} {ev.announcement}", expand=True))
            s = len(q & hay)
            if s:
                scored.append((s, ev))
        scored.sort(key=lambda t: (-t[0], t[1].date_iso))
        return [e for _, e in scored[:k]]

    # ---------- prompt material ----------
    def pages_index(self) -> str:
        lines = []
        for slug, (title, blurb) in PAGE_INFO.items():
            if slug in self.pages:
                lines.append(f"- {slug or '(αρχική)'} | {title} | {blurb} | {self.pages[slug].url}")
        return "\n".join(lines)

    def events_index(self) -> str:
        evs = sorted(self.events.values(), key=lambda e: e.date_iso or "9999")
        return "\n".join(
            f"- {e.anchor} | {e.date_text or '—'} | {e.title[:70]}"
            + (f" | {e.badge}" if e.badge else "")
            + (" | ΜΑΤΑΙΩΘΗΚΕ" if e.cancelled else "")
            for e in evs
        )

    def house_facts(self) -> str:
        return (
            f"Ιστότοπος: ΒΛΑΞ — {SITE_BASE_URL}/\n"
            "Τι είναι: πάρτι 80s που έγινε σκυλάδικο, στο Fuit Art Cafe (Ηλία Φάσσα 2, Γρεβενά), από το 2016.\n"
            "Τέσσερα ΒΛΑΞ έγιναν (vol.01 29/12/2016 – vol.04 28/12/2019). Το 2020 και το 2021 ματαιώθηκαν, τεκμηριωμένα.\n"
            "Οι δύο βλαξ: μπατζανάκια — «ο ηλίθιος» και «ο μπατίρης». Ονόματα: Στέργιος Χατζηκυριακίδης, Αλέξανδρος Χαντζής "
            "(ποιος είναι ποιος ΔΕΝ αποκαλύπτεται ποτέ).\n"
            "Το αρχείο κρατά και τα κενά: ό,τι δεν ξέρουμε, γράφεται ως άγνωστο."
        )


_KB: KnowledgeBase | None = None


def get_kb() -> KnowledgeBase:
    global _KB
    if _KB is None:
        _KB = KnowledgeBase()
    return _KB
