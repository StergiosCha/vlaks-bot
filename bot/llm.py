"""LLM providers behind one call: generate_reply(system, context, history, user) -> dict.

- GeminiProvider mirrors bpan_app's UniversalLLMManager: several keys
  (GEMINI_API_KEY, _2 … _10 / .api_key), a model priority list, per-(key, model)
  cooldowns and a final "panic" pass. Structured JSON via response_schema.
- ClaudeProvider uses the Anthropic SDK with structured outputs.

Both return a dict already validated against persona.REPLY_SCHEMA's required keys.
"""
from __future__ import annotations

import copy
import json
import logging
import re
import time
from typing import Any

import config
from personas import REPLY_SCHEMA, schema_reminder, system_prompt

log = logging.getLogger("vlax.llm")

Message = dict[str, str]  # {"role": "user"|"assistant", "content": str}


# ---------- shared helpers ----------
def _coerce(raw: str) -> dict:
    """Parse model JSON, tolerating code fences / leading prose."""
    txt = raw.strip()
    if txt.startswith("```"):
        txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt, flags=re.S)
    try:
        data = json.loads(txt)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", txt, re.S)
        if not m:
            raise
        data = json.loads(m.group(0))
    out = {
        "reply": str(data.get("reply", "")).strip(),
        "footnote": str(data.get("footnote") or "").strip(),
        "language": data.get("language") if data.get("language") in ("el", "en") else "el",
        "events": [str(x) for x in (data.get("events") or []) if x][:4],
        "page": str(data.get("page") or "").strip(),
        "quick_replies": [str(q) for q in (data.get("quick_replies") or []) if q][:4],
        "handoff": bool(data.get("handoff", False)),
    }
    if not out["reply"]:
        raise ValueError("empty reply")
    return out


def _history_text(history: list[Message]) -> str:
    if not history:
        return "(no previous messages)"
    return "\n".join(f"{'Επισκέπτης' if m['role']=='user' else 'Ξεναγός'}: {m['content']}" for m in history)


# ---------- Gemini (bpan pattern) ----------
class GeminiProvider:
    """Google Gemini via the `google-genai` SDK.

    Key types are auto-detected: `AIza…` = Google AI Studio key, `AQ.…` = Vertex AI
    Express-mode key (client created with vertexai=True). Rotation/fallback logic
    mirrors bpan_app's UniversalLLMManager.
    """

    name = "gemini"

    def __init__(self):
        from google import genai  # noqa: F401  (import check)
        self.keys = config.gemini_keys()
        self.models = list(config.GEMINI_MODELS)
        self.failed: dict[tuple[int, str], float] = {}
        self.cooldown = 60
        if not self.keys:
            raise RuntimeError("No Gemini API keys found (GEMINI_API_KEY / GEMINI_API_KEY_2… / .api_key)")
        self._clients: dict[int, Any] = {}
        log.info("Gemini provider: %d key(s), models=%s", len(self.keys), self.models)
        # Gemini's response_schema is a JSON-schema subset (no additionalProperties)
        self.schema = copy.deepcopy(REPLY_SCHEMA)
        self.schema.pop("additionalProperties", None)
        for prop in self.schema["properties"].values():
            prop.pop("additionalProperties", None)

    def _client(self, key_idx: int):
        from google import genai
        if key_idx not in self._clients:
            key = self.keys[key_idx]
            # Gemini Developer API (AI Studio) for all keys. Set GEMINI_VERTEX=1 only if your key
            # is a Vertex AI Express key and the Vertex AI API is enabled on its project.
            use_vertex = config.GEMINI_VERTEX and key.startswith("AQ.")
            self._clients[key_idx] = genai.Client(vertexai=True, api_key=key) if use_vertex else genai.Client(api_key=key)
        return self._clients[key_idx]

    def _combos(self) -> list[tuple[int, str]]:
        now = time.time()
        ordered = [(k, m) for m in self.models for k in range(len(self.keys)) if now - self.failed.get((k, m), 0) > self.cooldown]
        if not ordered:
            self.failed.clear()
            ordered = [(k, m) for m in self.models for k in range(len(self.keys))]
        return ordered

    def _call(self, key_idx: int, model_name: str, system: str, prompt: str) -> str:
        from google.genai import types

        client = self._client(key_idx)
        resp = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.3,
                top_p=0.9,
                max_output_tokens=1024,
                response_mime_type="application/json",
                response_schema=self.schema,
                http_options=types.HttpOptions(timeout=config.GEMINI_TIMEOUT * 1000),
                safety_settings=[
                    types.SafetySetting(category=c, threshold="BLOCK_ONLY_HIGH")
                    for c in ("HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH",
                              "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT")
                ],
            ),
        )
        text = getattr(resp, "text", None)
        if not text:
            raise ValueError("empty Gemini response")
        return text

    def generate(self, context: str, history: list[Message], user_msg: str, persona: str) -> dict:
        prompt = (
            f"{context}\n\n=== Η ΚΟΥΒΕΝΤΑ ΩΣ ΤΩΡΑ ===\n{_history_text(history)}\n\n"
            f"=== ΝΕΟ ΜΗΝΥΜΑ ΕΠΙΣΚΕΠΤΗ ===\n{user_msg}\n\n{schema_reminder()}"
        )
        last: Exception | None = None
        combos = self._combos()
        for attempt, (k, m) in enumerate(combos[:12]):
            try:
                log.info("Gemini attempt %d: model=%s key=%d", attempt + 1, m, k)
                return _coerce(self._call(k, m, system_prompt(persona), prompt))
            except Exception as e:  # noqa: BLE001
                last = e
                self.failed[(k, m)] = time.time()
                log.warning("Gemini %s/%d failed: %s", m, k, str(e)[:300])
                if "PERMISSION_DENIED" in str(e) or "SERVICE_DISABLED" in str(e) or "API key not valid" in str(e):
                    # not transient — the key/project is misconfigured; retrying other models won't help
                    raise RuntimeError(f"Gemini key rejected: {str(e)[:300]}") from e
                if "429" in str(e) or "ResourceExhausted" in type(e).__name__:
                    time.sleep(2)
        # panic pass, like bpan
        self.failed.clear()
        for k, m in self._combos():
            try:
                time.sleep(2)
                return _coerce(self._call(k, m, system_prompt(persona), prompt))
            except Exception as e:  # noqa: BLE001
                last = e
                self.failed[(k, m)] = time.time()
        raise RuntimeError(f"Gemini: all combos failed ({type(last).__name__ if last else 'unknown'}: {last})")


# ---------- Claude ----------
class ClaudeProvider:
    name = "claude"

    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = config.CLAUDE_MODEL

    def generate(self, context: str, history: list[Message], user_msg: str, persona: str) -> dict:
        import anthropic

        messages: list[dict[str, Any]] = [{"role": m["role"], "content": m["content"]} for m in history]
        messages.append({"role": "user", "content": f"{context}\n\n=== ΝΕΟ ΜΗΝΥΜΑ ΕΠΙΣΚΕΠΤΗ ===\n{user_msg}"})
        kwargs: dict[str, Any] = dict(
            model=self.model,
            max_tokens=config.CLAUDE_MAX_TOKENS,
            system=[{"type": "text", "text": system_prompt(persona), "cache_control": {"type": "ephemeral"}}],
            messages=messages,
            output_config={"effort": config.CLAUDE_EFFORT, "format": {"type": "json_schema", "schema": REPLY_SCHEMA}},
        )
        try:
            # Opus 5 / Fable 5: route safety-classifier declines to a fallback model server-side.
            resp = self.client.messages.create(
                **kwargs,
                extra_headers={"anthropic-beta": "server-side-fallback-2026-07-01"},
                extra_body={"fallbacks": "default"},
            )
        except anthropic.BadRequestError as e:
            if "fallbacks" not in str(e):
                raise
            resp = self.client.messages.create(**kwargs)
        if resp.stop_reason == "refusal":
            raise RuntimeError("Claude refused the request")
        text = next((b.text for b in resp.content if b.type == "text"), "")
        return _coerce(text)


_PROVIDER: GeminiProvider | ClaudeProvider | None = None


def get_provider():
    global _PROVIDER
    if _PROVIDER is None:
        if config.LLM_PROVIDER == "claude":
            _PROVIDER = ClaudeProvider()
        else:
            _PROVIDER = GeminiProvider()
    return _PROVIDER
