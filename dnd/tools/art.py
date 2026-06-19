#!/usr/bin/env python3
"""Replicate art generation for Ajiibwan scenarios.

Library + small CLI. Sends a text prompt to a Replicate image model and returns
the generated image bytes. Used by `art_review.py` (the local review web app) and
runnable standalone for one-offs.

Auth: reads REPLICATE_API_TOKEN from the environment, or from a gitignored `.env`
at the repo root or the campaign folder (KEY=VALUE lines).

Offline mode: set ART_FAKE=1 (or pass fake=True) to render a local placeholder
image with Pillow instead of calling the API — handy for building/testing the
review UI without a token or network.

CLI:
    .venv/bin/python dnd/tools/art.py --prompt "an ancient desert tower" \
        --out dnd/ajiibwan/build/art/test.png --aspect-ratio 3:4
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys

DEFAULT_MODEL = "bytedance/seedream-5-lite"

# Pixel dimensions used for placeholder images, keyed by aspect ratio.
_LONG_SIDE = 768


# --------------------------------------------------------------------------- env
def load_dotenv(*paths: str | os.PathLike) -> None:
    """Load KEY=VALUE pairs from the first existing .env, without overriding
    variables already set in the environment."""
    for p in paths:
        p = pathlib.Path(p)
        if not p.is_file():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip("'\"")
            os.environ.setdefault(key, val)
        return


def have_token() -> bool:
    return bool(os.environ.get("REPLICATE_API_TOKEN"))


# ------------------------------------------------------------------- generation
def _aspect_wh(aspect_ratio: str) -> tuple[int, int]:
    try:
        w, h = (float(x) for x in aspect_ratio.split(":"))
    except Exception:
        w, h = 3.0, 4.0
    if w >= h:
        return _LONG_SIDE, max(1, round(_LONG_SIDE * h / w))
    return max(1, round(_LONG_SIDE * w / h)), _LONG_SIDE


def _ext_from_bytes(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return "png"


def _placeholder(prompt: str, aspect_ratio: str, label: str = "") -> bytes:
    """Render a labelled placeholder PNG with Pillow (offline mode)."""
    from PIL import Image, ImageDraw, ImageFont
    import hashlib
    import io
    import textwrap

    w, h = _aspect_wh(aspect_ratio)
    seed = int(hashlib.sha1((label + prompt).encode()).hexdigest(), 16)
    bg = (60 + seed % 80, 50 + (seed >> 8) % 70, 70 + (seed >> 16) % 90)
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 18)
        big = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
    except Exception:
        font = big = ImageFont.load_default()
    d.rectangle([6, 6, w - 6, h - 6], outline=(255, 255, 255), width=2)
    y = 28
    if label:
        d.text((24, y), label, fill=(255, 255, 255), font=big)
        y += 44
    d.text((24, y), "[placeholder — ART_FAKE]", fill=(220, 220, 220), font=font)
    y += 36
    for line in textwrap.wrap(prompt.strip(), width=42)[:18]:
        d.text((24, y), line, fill=(235, 235, 235), font=font)
        y += 24
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _read_output(out) -> bytes:
    """Normalize a replicate.run() result to image bytes."""
    item = out[0] if isinstance(out, (list, tuple)) else out
    if hasattr(item, "read"):              # FileOutput (current client)
        return item.read()
    if isinstance(item, (bytes, bytearray)):
        return bytes(item)
    if isinstance(item, str):              # bare URL
        import urllib.request
        req = urllib.request.Request(item)
        tok = os.environ.get("REPLICATE_API_TOKEN")
        if tok and "api.replicate.com" in item:
            req.add_header("Authorization", f"Bearer {tok}")
        with urllib.request.urlopen(req) as r:  # noqa: S310 (trusted host)
            return r.read()
    raise TypeError(f"Unexpected Replicate output type: {type(item)!r}")


def generate(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    aspect_ratio: str = "3:4",
    size: str = "2K",
    reference_images: list[str] | None = None,
    label: str = "",
    fake: bool | None = None,
) -> tuple[bytes, str]:
    """Generate one image. Returns (image_bytes, file_extension)."""
    if fake is None:
        fake = os.environ.get("ART_FAKE") == "1" or not have_token()
    if fake:
        return _placeholder(prompt, aspect_ratio, label), "png"

    import replicate

    payload = {"prompt": prompt, "aspect_ratio": aspect_ratio, "size": size}
    if reference_images:
        payload["image_input"] = reference_images
    out = replicate.run(model, input=payload)
    data = _read_output(out)
    return data, _ext_from_bytes(data)


def generate_to_file(prompt: str, out_path: str | os.PathLike, **kw) -> pathlib.Path:
    data, ext = generate(prompt, **kw)
    out = pathlib.Path(out_path)
    if out.suffix.lstrip(".").lower() not in ("png", "jpg", "jpeg", "webp"):
        out = out.with_suffix("." + ext)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return out


# --------------------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    here = pathlib.Path(__file__).resolve()
    repo_root = here.parents[2]
    load_dotenv(repo_root / ".env", here.parents[1] / ".env")

    ap = argparse.ArgumentParser(description="Generate an image via Replicate.")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True, help="output image path")
    ap.add_argument("--model", default=os.environ.get("ART_MODEL", DEFAULT_MODEL))
    ap.add_argument("--aspect-ratio", default="3:4")
    ap.add_argument("--size", default="2K", choices=["2K", "3K"])
    ap.add_argument("--ref", action="append", default=None,
                    help="reference image URL (repeatable; image_input)")
    ap.add_argument("--fake", action="store_true", help="offline placeholder")
    args = ap.parse_args(argv)

    if not args.fake and not have_token():
        print("REPLICATE_API_TOKEN not set — use --fake for an offline placeholder, "
              "or export the token / add it to .env.", file=sys.stderr)
        return 2
    path = generate_to_file(
        args.prompt, args.out, model=args.model, aspect_ratio=args.aspect_ratio,
        size=args.size, reference_images=args.ref, fake=args.fake or None,
    )
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
