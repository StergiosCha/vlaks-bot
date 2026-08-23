"""Φτιάχνει τα avatars των τριών ξεναγών.

  python bot/make_avatar.py --generate kouts themis fuit   # παράγει masters με Gemini
  python bot/make_avatar.py --states themis                # παράγει εκφράσεις από το master (reference image)
  python bot/make_avatar.py                                # κόβει κυκλικά ό,τι υπάρχει

Αρχεία: bot/assets/<id>_master.png, bot/assets/<id>_<state>.png
Έξοδος: bot/assets/avatar/<id>_<state>_{48,64,96,128,256}.png|webp
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

SIZES = (48, 64, 96, 128, 256)
STATES = ["idle", "thinking", "talking", "wave", "sorry"]

STYLE_TAIL = (
    "Head-and-shoulders, looking straight at camera, centred, plenty of headroom. Solid warm off-white "
    "background, soft studio lighting, subsurface scattering skin, subtle pores and hair strands, clean "
    "readable silhouette. Octane render, 4k, square 1:1. No text anywhere in the image."
)

MASTERS = {
    "kouts": (
        "3D stylised character portrait, Pixar/DreamWorks style, semi-realistic. Giorgos, Greek man late 30s: "
        "enormous, heavyset gentle giant — very broad shoulders and thick neck filling the frame, round belly "
        "hinted below, big soft face. Completely bald shiny head, full thick dark beard neatly trimmed, thick "
        "eyebrows, warm kind eyes, friendly grin. Plain black t-shirt. " + STYLE_TAIL
    ),
    "themis": (
        "3D stylised character portrait, Pixar/DreamWorks style, semi-realistic. Themis, Greek man in his early "
        "40s: lean and wiry, narrow shoulders, alert upright posture. Short dark hair pushed back, three-day "
        "stubble, sharp cheekbones, thick dark eyebrows raised in permanent mild diagnosis. Bright, intense, "
        "slightly manic but kind eyes behind clear round wire glasses; a wide confident grin showing "
        "conspicuously perfect white teeth. Wearing a rumpled white doctor's coat thrown over a black party "
        "shirt with the collar open, a stethoscope hanging casually around his neck like a scarf. " + STYLE_TAIL
    ),
    "fuit": (
        "3D stylised character portrait, Pixar/DreamWorks style, semi-realistic. Giannis, Greek man in his late "
        "40s: medium build, slightly stooped from years behind a bar, broad friendly face weathered by mountain "
        "winters. Long dark wavy hair falling past his shoulders, streaked with grey, tucked behind one ear; a "
        "full untrimmed salt-and-pepper beard. Deep laugh lines, heavy-lidded warm brown eyes with an amused, "
        "half-complaining expression, one eyebrow slightly raised. Wearing a worn dark denim shirt with sleeves "
        "rolled up over a faded band t-shirt, a bartender's apron strap visible on one shoulder. The brass bell "
        "of a trombone catches the light at the bottom edge of the frame, just below his shoulder. " + STYLE_TAIL
    ),
}

STATE_EDITS = {
    "wave": "raising one open hand in a small greeting beside the face, warmer smile",
    "thinking": {
        "kouts": "eyes glancing up and to the side, hand on the back of his bald head, mouth closed, concentrating",
        "themis": "eyes glancing up and to the side, pressing two fingers to the side of his own neck as if taking his pulse, concentrating",
        "fuit": "eyes shut, pinching the bridge of his nose mid-sigh, concentrating",
    },
    "talking": "mouth open mid-word, eyebrows lifted, animated and engaged",
    "sorry": "apologetic expression, slight shrug, both palms turned up at chest height",
}

IMAGE_MODELS = ["gemini-3-pro-image", "gemini-3.1-flash-image", "gemini-2.5-flash-image"]


def _client():
    from google import genai
    keys = config.gemini_keys()
    if not keys:
        raise SystemExit("Δεν βρέθηκε GEMINI_API_KEY (bot/.env)")
    return genai.Client(api_key=keys[0])


def _generate(prompt: str, reference: Path | None = None) -> bytes:
    from google.genai import types
    client = _client()
    contents: list = [prompt]
    if reference and reference.exists():
        contents.insert(0, types.Part.from_bytes(data=reference.read_bytes(), mime_type="image/png"))
    last = None
    for model in IMAGE_MODELS:
        try:
            resp = client.models.generate_content(model=model, contents=contents)
            for cand in resp.candidates or []:
                for part in cand.content.parts or []:
                    inline = getattr(part, "inline_data", None)
                    if inline and inline.data:
                        print(f"    [{model}]")
                        return inline.data
            last = RuntimeError(f"{model}: no image part")
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"    [{model}] {str(e)[:110]}")
    raise RuntimeError(f"image generation failed: {last}")


def circular(img: Image.Image, size: int) -> Image.Image:
    im = img.resize((size, size), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    im.putalpha(mask.resize((size, size), Image.LANCZOS))
    return im


def crop_head(img: Image.Image, head: float, top: float) -> Image.Image:
    w, h = img.size
    side = int(min(w, h) * head)
    t = int(h * top)
    return img.crop(((w - side) // 2, t, (w - side) // 2 + side, t + side))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", nargs="*", metavar="ID", help="παράγει masters (kouts themis fuit)")
    ap.add_argument("--states", nargs="*", metavar="ID", help="παράγει εκφράσεις από τα masters")
    ap.add_argument("--head", type=float, default=0.86)
    ap.add_argument("--top", type=float, default=0.04)
    args = ap.parse_args()

    assets = config.ASSETS_DIR
    assets.mkdir(parents=True, exist_ok=True)

    for pid in args.generate or []:
        if pid not in MASTERS:
            print(f"[skip] άγνωστος χαρακτήρας: {pid}")
            continue
        print(f"[gen] master {pid}")
        data = _generate(MASTERS[pid])
        (assets / f"{pid}_master.png").write_bytes(data)
        print(f"  → {assets / f'{pid}_master.png'}")

    for pid in args.states or []:
        master = assets / f"{pid}_master.png"
        if not master.exists():
            print(f"[skip] λείπει {master}")
            continue
        for state, edit in STATE_EDITS.items():
            e = edit[pid] if isinstance(edit, dict) else edit
            print(f"[gen] {pid}/{state}")
            prompt = ("Keep exactly this same 3D stylised character: same face, same hair, same clothes, same "
                      "framing, same warm off-white background, same lighting and render style. Change only the "
                      f"expression and pose: {e}. Square 1:1, no text in the image.")
            try:
                (assets / f"{pid}_{state}.png").write_bytes(_generate(prompt, reference=master))
            except Exception as ex:  # noqa: BLE001
                print(f"  ! {ex}")

    out = assets / "avatar"
    out.mkdir(parents=True, exist_ok=True)
    made = 0
    for pid in MASTERS:
        for state in STATES:
            src = assets / (f"{pid}_master.png" if state == "idle" else f"{pid}_{state}.png")
            if not src.exists():
                continue
            head = crop_head(Image.open(src).convert("RGBA"), args.head, args.top)
            for s in SIZES:
                c = circular(head, s)
                c.save(out / f"{pid}_{state}_{s}.png", optimize=True)
                c.save(out / f"{pid}_{state}_{s}.webp", quality=90, method=6)
            made += 1
    print(f"[ok] κυκλικά avatars για {made} καταστάσεις → {out}")


if __name__ == "__main__":
    main()
