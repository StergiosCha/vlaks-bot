"""Φτιάχνει το widget/embed.js από το widget/index.html.

Το index.html είναι η μία πηγή αλήθειας του widget· το embed.js είναι η ίδια δουλειά
τυλιγμένη σε injection, για να μπει στο Astro site με μία γραμμή <script>.

    venv/bin/python bot/build_embed.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import WIDGET_DIR  # noqa: E402

html = (WIDGET_DIR / "index.html").read_text(encoding="utf-8")

css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
script = re.search(r"<script>\s*\(function\(\)\{(.*?)\}\)\(\);\s*</script>", html, re.S).group(1)
fonts = re.findall(r'<link href="(https://fonts\.googleapis\.com[^"]+)"', html)

# όλα τα κομμάτια του widget εκτός της σελίδας επίδειξης (.demo)
markup = "".join(
    m.group(0) for m in re.finditer(r'<(button id="vx-launcher".*?</button>|section id="vx".*?</section>)', html, re.S)
)

embed = f"""/* ΒΛΑΞ — ο ξεναγός. Παράγεται από widget/index.html (bot/build_embed.py). Μην το επεξεργάζεσαι με το χέρι. */
(function () {{
  if (window.__vlaxGuideLoaded) return;
  window.__vlaxGuideLoaded = true;

  var FONTS = {json.dumps(fonts)};
  FONTS.forEach(function (href) {{
    if (document.querySelector('link[href="' + href + '"]')) return;
    var l = document.createElement('link'); l.rel = 'stylesheet'; l.href = href; document.head.appendChild(l);
  }});

  var style = document.createElement('style');
  style.textContent = {json.dumps(css)};
  document.head.appendChild(style);

  var host = document.createElement('div');
  host.id = 'vlax-guide-root';
  host.innerHTML = {json.dumps(markup)};
  document.body.appendChild(host);

  (function () {{{script}}})();
}})();
"""
out = WIDGET_DIR / "embed.js"
out.write_text(embed, encoding="utf-8")
print(f"[ok] {out} ({len(embed) // 1024} KB) — markup {len(markup)}B, css {len(css)}B, script {len(script)}B")
