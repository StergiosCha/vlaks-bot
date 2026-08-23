"""Προστασία του δημόσιου /chat.

Το endpoint είναι ανοιχτό στον κόσμο και κάθε κλήση ξοδεύει κουότα Gemini. Το CORS δεν
προστατεύει από `curl` — μόνο από browsers. Οπότε:

  1. token bucket ανά IP     (πόσο γρήγορα μιλάει ένας)
  2. ημερήσιο πλαφόν κλήσεων (πόσο μπορεί να μας κοστίσει μια κακή μέρα, συνολικά)

Όλα στη μνήμη: ταιριάζει με ένα instance, που είναι έτσι κι αλλιώς η ανάπτυξη που θέλουμε.
"""
from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass, field

# Πόσα μηνύματα επιτρέπονται σε ένα παράθυρο, ανά IP.
PER_IP_MESSAGES = int(os.environ.get("RL_PER_IP_MESSAGES", "20"))
PER_IP_WINDOW_S = int(os.environ.get("RL_PER_IP_WINDOW", "600"))     # 10 λεπτά
# Συνολικό ημερήσιο πλαφόν κλήσεων στο μοντέλο (όλοι οι επισκέπτες μαζί).
DAILY_CAP = int(os.environ.get("RL_DAILY_CAP", "600"))
# Ταυτόχρονες κλήσεις — μια μικρή ουρά είναι φθηνότερη από ένα τείχος 429.
MAX_CONCURRENT = int(os.environ.get("RL_MAX_CONCURRENT", "4"))


@dataclass
class _Bucket:
    tokens: float
    last: float


@dataclass
class Limiter:
    per_ip: int = PER_IP_MESSAGES
    window: int = PER_IP_WINDOW_S
    daily_cap: int = DAILY_CAP
    _buckets: dict[str, _Bucket] = field(default_factory=dict)
    _day: str = ""
    _day_count: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _sem: threading.Semaphore = field(default_factory=lambda: threading.Semaphore(MAX_CONCURRENT))

    def _today(self) -> str:
        return time.strftime("%Y-%m-%d", time.gmtime())

    def check(self, ip: str) -> tuple[bool, str]:
        """(επιτρέπεται;, λόγος). Ο λόγος είναι 'ip' ή 'daily'."""
        now = time.time()
        with self._lock:
            day = self._today()
            if day != self._day:
                self._day, self._day_count = day, 0
            if self._day_count >= self.daily_cap:
                return False, "daily"

            b = self._buckets.get(ip)
            rate = self.per_ip / self.window          # tokens ανά δευτερόλεπτο
            if b is None:
                b = _Bucket(tokens=float(self.per_ip), last=now)
                self._buckets[ip] = b
            else:
                b.tokens = min(float(self.per_ip), b.tokens + (now - b.last) * rate)
                b.last = now
            if b.tokens < 1.0:
                return False, "ip"
            b.tokens -= 1.0
            self._day_count += 1

            if len(self._buckets) > 5000:            # φρένο μνήμης· πετάμε ό,τι έχει ξαναγεμίσει
                stale = [k for k, v in self._buckets.items() if v.tokens >= self.per_ip - 0.01]
                for k in stale[: len(stale) // 2 or 1]:
                    self._buckets.pop(k, None)
            return True, ""

    def refund(self, ip: str) -> None:
        """Αν η κλήση απέτυχε πριν φτάσει στο μοντέλο, μην τη χρεώσεις στον επισκέπτη."""
        with self._lock:
            b = self._buckets.get(ip)
            if b:
                b.tokens = min(float(self.per_ip), b.tokens + 1.0)
            if self._day_count > 0:
                self._day_count -= 1

    def stats(self) -> dict:
        with self._lock:
            return {"day": self._day or self._today(), "used_today": self._day_count,
                    "daily_cap": self.daily_cap, "tracked_ips": len(self._buckets),
                    "per_ip": f"{self.per_ip}/{self.window}s"}

    def slot(self):
        return self._sem


def client_ip(request) -> str:
    """Το πραγματικό IP πίσω από proxy (Render/HF/Cloud Run βάζουν X-Forwarded-For)."""
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        return xff.split(",")[0].strip()
    return (request.client.host if request.client else "unknown")
