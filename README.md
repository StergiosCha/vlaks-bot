# vlaks-bot — ο ξεναγός του ΒΛΑΞ

Το backend του chat για το [ΒΛΑΞ](https://stergioscha.github.io/vlaks/). Τρεις ξεναγοί —
**Κουτς** ο γίγαντας, **Θέμης** ο γιατρός, **Μπάλκαν Φούιτ** ο οικοδεσπότης — απαντούν από
το αρχείο του site, με υποσημείωση και κάρτες γεγονότων.

Ο κώδικας του αρχείου ζει στο [StergiosCha/vlaks](https://github.com/StergiosCha/vlaks)·
εδώ είναι μόνο ό,τι χρειάζεται για να τρέχει ο ξεναγός σε έναν server.

## Deploy (Render, free)

1. New → Blueprint → αυτό το repo. Το `render.yaml` τα ορίζει όλα.
2. Στο dashboard βάλε το `GEMINI_API_KEY` (Environment → Add). Ποτέ στο git.
3. Το widget στο site: `<script src="https://<service>.onrender.com/widget/embed.js" defer></script>`
   με `window.VLAX_API="https://<service>.onrender.com";` από πάνω.

**Free tier:** 750 ώρες/μήνα για όλο το workspace, ύπνος μετά από 15′ ησυχίας, ~1′ για να
ξυπνήσει. Το widget στέλνει ένα `GET /health` μόλις ο επισκέπτης πλησιάσει το κουμπί, οπότε
ο ξεναγός ξυπνάει όσο εκείνος διαβάζει. Το `/health` δεν καλεί μοντέλο.

## Ανανέωση του αρχείου

Το KB είναι ψημένο στο `bot/kb_cache.json` (429 KB) — έτσι δεν χρειάζεται εδώ ολόκληρο το
`site/dist` (225 MB). Όταν αλλάξει το site:

```bash
cd ~/Dropbox/vlax-archive/site && npm run build
cd .. && venv/bin/python bot/build_kb_cache.py
# αντέγραψε το νέο bot/kb_cache.json εδώ και κάνε commit
```

## Τοπικά

```bash
pip install -r bot/requirements.txt
cp bot/.env.example bot/.env      # βάλε το GEMINI_API_KEY
uvicorn server:app --app-dir bot --port 8788
```

Τεκμηρίωση: [bot/README.md](bot/README.md) · avatars: [bot/AVATAR_PROMPTS.md](bot/AVATAR_PROMPTS.md)
