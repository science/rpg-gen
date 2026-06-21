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
import time

DEFAULT_MODEL = "bytedance/seedream-5-lite"

# Pixel dimensions used for placeholder images, keyed by aspect ratio.
_LONG_SIDE = 768


# --------------------------------------------------------------------------- env
# Accept common alternate key names for the Replicate token.
_KEY_ALIASES = {"REPLICATE_API_KEY": "REPLICATE_API_TOKEN"}


def load_dotenv(*paths: str | os.PathLike) -> None:
    """Load KEY=VALUE pairs from every existing file given, without overriding
    variables already set in the environment (earlier files/env win). Known
    aliases (e.g. replicate_api_key) are mapped to REPLICATE_API_TOKEN."""
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
            key = _KEY_ALIASES.get(key.upper(), key)
            os.environ.setdefault(key, val)
    for src, dst in _KEY_ALIASES.items():
        if os.environ.get(src) and not os.environ.get(dst):
            os.environ[dst] = os.environ[src]


def have_token() -> bool:
    return bool(os.environ.get("REPLICATE_API_TOKEN"))


def have_token_for(provider: str) -> bool:
    if provider == "openai":
        return bool(os.environ.get("OPENAI_API_KEY"))
    return have_token()  # replicate


# --------------------------------------------------------------- model registry
# Selectable models across providers. `prompts.yaml` may add/override via `models:`;
# the seed `model:` stays the default selection. i2i = supports image-to-image.
MODEL_REGISTRY = [
    {"id": "bytedance/seedream-5-lite", "label": "Seedream 5 Lite (Replicate)",
     "provider": "replicate", "i2i": True, "sizes": ["2K", "3K"]},
    {"id": "bytedance/seedream-4.5", "label": "Seedream 4.5 (Replicate)",
     "provider": "replicate", "i2i": True, "sizes": ["2K", "4K"]},
    {"id": "gpt-image-2", "label": "GPT-Image-2 (OpenAI)",
     "provider": "openai", "i2i": True, "sizes": ["auto"]},
]
_REGISTRY_BY_ID = {m["id"]: m for m in MODEL_REGISTRY}


def model_meta(model_id: str) -> dict:
    """Registry entry for a model id; unknown ids fall back to a replicate default."""
    return _REGISTRY_BY_ID.get(
        model_id,
        {"id": model_id, "label": model_id, "provider": "replicate",
         "i2i": True, "sizes": ["2K"]})


def provider_for(model_id: str) -> str:
    return model_meta(model_id)["provider"]


# OpenAI gpt-image uses pixel sizes, not aspect strings — map the UI aspect choice.
def _aspect_to_openai_size(aspect_ratio: str) -> str:
    try:
        w, h = (float(x) for x in aspect_ratio.split(":"))
    except Exception:
        w, h = 1.0, 1.0
    if w > h:
        return "1536x1024"   # landscape
    if h > w:
        return "1024x1536"   # portrait
    return "1024x1024"       # square


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


def _build_payload(
    prompt: str,
    *,
    aspect_ratio: str,
    size: str,
    reference_images: list[str] | None = None,
) -> dict:
    """Assemble the Replicate `input` dict. The chosen aspect_ratio/size MUST
    be carried through verbatim (regression guard for the 'always 3:2' report)."""
    payload = {"prompt": prompt, "aspect_ratio": aspect_ratio, "size": size}
    if reference_images:
        payload["image_input"] = reference_images
    return payload


def _get_client():
    import replicate
    return replicate.Client(api_token=os.environ.get("REPLICATE_API_TOKEN"))


def _file_to_data_uri(path: str | os.PathLike) -> str:
    """Encode a local image as a data URI (for Replicate image_input — no upload)."""
    import base64
    data = pathlib.Path(path).read_bytes()
    ext = _ext_from_bytes(data)
    mime = {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
    return f"data:{mime};base64," + base64.b64encode(data).decode()


class LiveHandle:
    """Wraps a Replicate Prediction; `poll()` refreshes and normalizes it."""

    def __init__(self, prediction):
        self.pred = prediction

    def poll(self) -> dict:
        p = self.pred
        try:
            p.reload()
        except Exception:  # noqa: BLE001 — a transient reload failure is not fatal
            pass
        status = getattr(p, "status", None) or "starting"
        logs = getattr(p, "logs", "") or ""
        error = getattr(p, "error", None)
        progress = _live_progress(p)
        out_bytes = ext = None
        if status == "succeeded":
            out = getattr(p, "output", None)
            if out is not None:
                out_bytes = _read_output(out)
                ext = _ext_from_bytes(out_bytes)
        return {"status": status, "logs": logs, "progress": progress,
                "error": str(error) if error else None,
                "output_bytes": out_bytes, "ext": ext}


def _live_progress(pred) -> float | None:
    prog = getattr(pred, "progress", None)
    pct = getattr(prog, "percentage", None)
    try:
        return float(pct) if pct is not None else None
    except (TypeError, ValueError):
        return None


class FakeHandle:
    """Offline stand-in that simulates starting -> processing -> succeeded over
    `delay` seconds and yields a Pillow placeholder. delay=0 -> instant success."""

    def __init__(self, prompt, *, aspect_ratio="3:4", label="", delay=0.0):
        self.prompt = prompt
        self.aspect_ratio = aspect_ratio
        self.label = label
        self.delay = delay
        self._t0 = time.time()

    def poll(self) -> dict:
        elapsed = time.time() - self._t0
        if elapsed < self.delay * 0.5:
            return {"status": "starting", "logs": "", "progress": 0.0,
                    "error": None, "output_bytes": None, "ext": None}
        if elapsed < self.delay:
            return {"status": "processing", "logs": "rendering (placeholder)",
                    "progress": 0.5, "error": None, "output_bytes": None, "ext": None}
        data = _placeholder(self.prompt, self.aspect_ratio, self.label)
        return {"status": "succeeded", "logs": "done", "progress": 1.0,
                "error": None, "output_bytes": data, "ext": "png"}


class OpenAIHandle:
    """Runs an OpenAI gpt-image generate/edit call in a background thread so the
    JobManager's poll loop stays responsive. poll() reports `processing` until the
    thread finishes, then `succeeded` with decoded bytes (or `failed` + error)."""

    def __init__(self, prompt, *, model, aspect_ratio, reference_images=None,
                 quality="high", client=None):
        import threading
        self._lock = threading.Lock()
        self._status = "starting"
        self._bytes = None
        self._error = None
        self._size = _aspect_to_openai_size(aspect_ratio)
        self._t = threading.Thread(
            target=self._work,
            args=(prompt, model, self._size, quality, reference_images, client),
            daemon=True)
        self._t.start()

    def _work(self, prompt, model, size, quality, reference_images, client):
        try:
            if client is None:
                from openai import OpenAI
                client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            if reference_images:
                files = [open(p, "rb") for p in reference_images]
                try:
                    resp = client.images.edit(model=model, image=files,
                                              prompt=prompt, size=size)
                finally:
                    for f in files:
                        f.close()
            else:
                resp = client.images.generate(model=model, prompt=prompt,
                                              size=size, quality=quality)
            data = _openai_bytes(resp)
            with self._lock:
                self._bytes, self._status = data, "succeeded"
        except Exception as e:  # noqa: BLE001 — surface to the UI as a failed job
            with self._lock:
                self._error, self._status = str(e), "failed"

    def poll(self) -> dict:
        with self._lock:
            status, data, err = self._status, self._bytes, self._error
        if status == "succeeded":
            return {"status": "succeeded", "logs": "", "progress": 1.0,
                    "error": None, "output_bytes": data, "ext": _ext_from_bytes(data)}
        if status == "failed":
            return {"status": "failed", "logs": "", "progress": None,
                    "error": err, "output_bytes": None, "ext": None}
        return {"status": "processing", "logs": "", "progress": None,
                "error": None, "output_bytes": None, "ext": None}


def _openai_bytes(resp) -> bytes:
    """Extract image bytes from an OpenAI images response (b64 or url)."""
    import base64
    item = resp.data[0]
    b64 = getattr(item, "b64_json", None)
    if b64:
        return base64.b64decode(b64)
    url = getattr(item, "url", None)
    if url:
        return _read_output(url)
    raise TypeError("OpenAI image response had neither b64_json nor url")


def _is_fake(fake: bool | None, provider: str = "replicate") -> bool:
    if fake is None:
        return os.environ.get("ART_FAKE") == "1" or not have_token_for(provider)
    return fake


def submit(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    aspect_ratio: str = "3:4",
    size: str = "2K",
    reference_images: list[str] | None = None,
    label: str = "",
    fake: bool | None = None,
    delay: float = 0.0,
    client=None,
):
    """Start a generation and return a poll-able handle immediately (non-blocking).

    Routes by the model's provider (Replicate predictions API, or OpenAI gpt-image).
    `reference_images` (local paths) triggers image-to-image. Fake mode returns a
    FakeHandle; `delay` affects only fake handles; `client` is injectable for tests."""
    provider = provider_for(model)
    if _is_fake(fake, provider):
        return FakeHandle(prompt, aspect_ratio=aspect_ratio, label=label, delay=delay)
    if provider == "openai":
        return OpenAIHandle(prompt, model=model, aspect_ratio=aspect_ratio,
                            reference_images=reference_images, client=client)
    # replicate
    refs = [_file_to_data_uri(p) for p in reference_images] if reference_images else None
    payload = _build_payload(prompt, aspect_ratio=aspect_ratio, size=size,
                             reference_images=refs)
    client = client or _get_client()
    pred = client.predictions.create(model=model, input=payload)
    return LiveHandle(pred)


def poll(handle) -> dict:
    """Return {status, logs, progress, error, output_bytes, ext} for a handle."""
    return handle.poll()


def generate(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    aspect_ratio: str = "3:4",
    size: str = "2K",
    reference_images: list[str] | None = None,
    label: str = "",
    fake: bool | None = None,
    poll_interval: float = 0.5,
) -> tuple[bytes, str]:
    """Blocking convenience: submit, then poll until done. Returns (bytes, ext)."""
    handle = submit(prompt, model=model, aspect_ratio=aspect_ratio, size=size,
                    reference_images=reference_images, label=label, fake=fake)
    while True:
        r = poll(handle)
        if r["status"] == "succeeded":
            return r["output_bytes"], r["ext"] or _ext_from_bytes(r["output_bytes"])
        if r["status"] in ("failed", "canceled"):
            raise RuntimeError(f"generation {r['status']}: {r.get('error')}")
        time.sleep(poll_interval)


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
    load_dotenv(repo_root / "credentials" / "env.production",
                repo_root / ".env", here.parents[1] / ".env")

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
