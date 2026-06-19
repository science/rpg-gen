#!/usr/bin/env python3
"""Local web app to review / regenerate / accept Ajiibwan scenario art.

Workflow per subject (from <campaign>/art/prompts.yaml):
  - see the current image and the prompt,
  - tweak the prompt (and aspect ratio) and hit Generate for another "turn",
  - Accept the turn you like (marks it as the chosen image).

State lives in <campaign>/build/art/gallery.json (gitignored); images are saved
alongside it as <id>-tNN.<ext>. Generation goes through tools/art.py, which uses
Replicate when REPLICATE_API_TOKEN is set and offline Pillow placeholders otherwise
(or when ART_FAKE=1).

Run:
    .venv/bin/python dnd/tools/art_review.py ajiibwan            # http://<host>:5005
    .venv/bin/python dnd/tools/art_review.py ajiibwan --port 5005 --fake
"""
from __future__ import annotations

import argparse
import json
import pathlib

import yaml
from flask import (Flask, abort, flash, redirect, render_template_string,
                   request, send_from_directory, url_for)

import art  # sibling module (tools/art.py)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

app = Flask(__name__)
app.secret_key = "ajiibwan-art-review"  # local single-user tool

# Set at startup by main().
PATHS: dict[str, pathlib.Path] = {}
SEED: dict = {}


# ------------------------------------------------------------------ state I/O
def load_state() -> dict:
    gp = PATHS["gallery"]
    state = json.loads(gp.read_text()) if gp.is_file() else {"subjects": {}}
    # Refresh top-level config + merge in any new subjects from the seed yaml.
    state["model"] = SEED.get("model", art.DEFAULT_MODEL)
    state["size"] = SEED.get("size", "2K")
    state["style"] = (SEED.get("style") or "").strip()
    subs = state.setdefault("subjects", {})
    for s in SEED.get("subjects", []):
        if s["id"] not in subs:
            subs[s["id"]] = {
                "label": s.get("label", s["id"]),
                "aspect_ratio": s.get("aspect_ratio", "3:4"),
                "prompt": (s.get("prompt") or "").strip(),
                "accepted": None,
                "turns": [],
            }
    return state


def save_state(state: dict) -> None:
    PATHS["gallery"].write_text(json.dumps(state, indent=2))


def effective_prompt(state: dict, subj: dict) -> str:
    style = state.get("style", "")
    return f"{style}\n\n{subj['prompt']}".strip() if style else subj["prompt"]


# ---------------------------------------------------------------------- views
@app.route("/")
def index():
    state = load_state()
    return render_template_string(TEMPLATE, state=state, have_token=art.have_token())


@app.route("/art/<path:filename>")
def art_file(filename):
    return send_from_directory(PATHS["artdir"], filename)


@app.route("/generate", methods=["POST"])
def generate():
    state = load_state()
    sid = request.form["id"]
    subj = state["subjects"].get(sid) or abort(404)
    subj["prompt"] = request.form.get("prompt", subj["prompt"]).strip()
    subj["aspect_ratio"] = request.form.get("aspect_ratio", subj["aspect_ratio"])
    n = len(subj["turns"]) + 1
    fname = f"{sid}-t{n:02d}"
    try:
        out = art.generate_to_file(
            effective_prompt(state, subj),
            PATHS["artdir"] / fname,
            model=state["model"],
            aspect_ratio=subj["aspect_ratio"],
            size=state.get("size", "2K"),
            label=subj["label"],
        )
    except Exception as e:  # noqa: BLE001 — surface any API/client error to the UI
        flash(f"[{sid}] generation failed: {e}")
        save_state(state)
        return redirect(url_for("index") + f"#{sid}")
    subj["turns"].append({
        "n": n, "file": out.name, "prompt": subj["prompt"],
        "aspect_ratio": subj["aspect_ratio"], "fake": not art.have_token(),
    })
    save_state(state)
    flash(f"[{sid}] generated turn {n}" + (" (placeholder)" if not art.have_token() else ""))
    return redirect(url_for("index") + f"#{sid}")


@app.route("/accept", methods=["POST"])
def accept():
    state = load_state()
    sid = request.form["id"]
    subj = state["subjects"].get(sid) or abort(404)
    subj["accepted"] = request.form["file"]
    save_state(state)
    flash(f"[{sid}] accepted {subj['accepted']}")
    return redirect(url_for("index") + f"#{sid}")


# ------------------------------------------------------------------- template
TEMPLATE = """
<!doctype html><html><head><meta charset="utf-8"><title>Ajiibwan art review</title>
<style>
 :root{color-scheme:dark}
 body{background:#16131a;color:#e8e4ee;font:15px/1.45 system-ui,sans-serif;margin:0}
 header{padding:14px 22px;background:#221c2b;border-bottom:1px solid #3a3145;position:sticky;top:0;z-index:5}
 header h1{font-size:18px;margin:0 0 4px}
 .tok{font-size:13px} .ok{color:#7fd18b} .warn{color:#e6c06a}
 .flash{margin:8px 22px;padding:8px 12px;background:#2c2336;border:1px solid #463a55;border-radius:6px;font-size:13px}
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:18px;padding:18px 22px}
 .card{background:#1f1b27;border:1px solid #352c42;border-radius:10px;padding:14px}
 .card h3{margin:0 0 8px;font-size:15px}.card h3 small{color:#9a8fae;font-weight:400}
 .cur{width:100%;aspect-ratio:3/4;object-fit:cover;background:#0d0b11;border-radius:8px;border:1px solid #352c42}
 .none{display:flex;align-items:center;justify-content:center;color:#6f6680;height:220px}
 .badge{display:inline-block;font-size:11px;padding:1px 7px;border-radius:10px;background:#2e4a32;color:#9be0a6;margin-left:6px}
 textarea{width:100%;box-sizing:border-box;background:#161320;color:#e8e4ee;border:1px solid #3a3145;border-radius:6px;padding:8px;font:13px/1.4 ui-monospace,monospace;resize:vertical;min-height:96px}
 .row{display:flex;gap:8px;align-items:center;margin-top:8px;flex-wrap:wrap}
 select,button{background:#2b2336;color:#e8e4ee;border:1px solid #463a55;border-radius:6px;padding:7px 11px;font-size:13px;cursor:pointer}
 button.go{background:#3b2f57;border-color:#5b4a83}
 button.acc{background:#274a2c;border-color:#3c7044}
 .film{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}
 .film figure{margin:0;width:74px;text-align:center}
 .film img{width:74px;height:74px;object-fit:cover;border-radius:5px;border:1px solid #352c42;display:block}
 .film .on{border-color:#7fd18b;border-width:2px}
 .film button{padding:2px 6px;font-size:11px;margin-top:3px;width:100%}
 .film figcaption{font-size:10px;color:#9a8fae}
</style></head><body>
<header>
  <h1>Deserts of Ajiibwan — art review</h1>
  <div class="tok">
    {% if have_token %}<span class="ok">● REPLICATE_API_TOKEN detected — live generation ({{state.model}}, {{state.size}})</span>
    {% else %}<span class="warn">● No token — offline placeholders. Set REPLICATE_API_TOKEN (or .env) for real images.</span>{% endif %}
  </div>
</header>
{% with msgs = get_flashed_messages() %}{% for m in msgs %}<div class="flash">{{m}}</div>{% endfor %}{% endwith %}
<div class="grid">
{% for sid, s in state.subjects.items() %}
  {% set cur = s.accepted or (s.turns[-1].file if s.turns else None) %}
  <div class="card" id="{{sid}}">
    <h3>{{s.label}} <small>{{sid}}</small>{% if s.accepted %}<span class="badge">accepted</span>{% endif %}</h3>
    {% if cur %}<img class="cur" src="{{url_for('art_file',filename=cur)}}" alt="{{sid}}">
    {% else %}<div class="cur none">no image yet — Generate</div>{% endif %}
    <form method="post" action="{{url_for('generate')}}">
      <input type="hidden" name="id" value="{{sid}}">
      <div class="row"><textarea name="prompt">{{s.prompt}}</textarea></div>
      <div class="row">
        <select name="aspect_ratio">
          {% for ar in ['1:1','4:3','3:4','16:9','9:16','3:2','2:3','21:9'] %}
          <option value="{{ar}}" {{'selected' if ar==s.aspect_ratio else ''}}>{{ar}}</option>{% endfor %}
        </select>
        <button class="go" type="submit">Generate{% if not have_token %} (placeholder){% endif %}</button>
        <span style="color:#9a8fae;font-size:12px">{{s.turns|length}} turn(s)</span>
      </div>
    </form>
    {% if s.turns %}
    <div class="film">
      {% for t in s.turns %}
      <figure>
        <img class="{{'on' if t.file==s.accepted else ''}}" src="{{url_for('art_file',filename=t.file)}}" title="turn {{t.n}}: {{t.prompt}}">
        <form method="post" action="{{url_for('accept')}}">
          <input type="hidden" name="id" value="{{sid}}"><input type="hidden" name="file" value="{{t.file}}">
          <button class="acc" type="submit">{{'✓' if t.file==s.accepted else 'accept'}}</button>
        </form>
        <figcaption>t{{t.n}}{{' (ph)' if t.fake else ''}}</figcaption>
      </figure>
      {% endfor %}
    </div>{% endif %}
  </div>
{% endfor %}
</div></body></html>
"""


# ------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description="Local art review web app.")
    ap.add_argument("campaign", nargs="?", default="ajiibwan")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=5005)
    ap.add_argument("--fake", action="store_true",
                    help="force offline placeholder generation")
    args = ap.parse_args(argv)

    base = REPO_ROOT / "dnd" / args.campaign
    art.load_dotenv(REPO_ROOT / ".env", base / ".env")
    if args.fake:
        import os
        os.environ["ART_FAKE"] = "1"

    global SEED, PATHS
    prompts_file = base / "art" / "prompts.yaml"
    SEED = yaml.safe_load(prompts_file.read_text()) if prompts_file.is_file() else {}
    artdir = base / "build" / "art"
    artdir.mkdir(parents=True, exist_ok=True)
    PATHS = {"base": base, "prompts": prompts_file, "artdir": artdir,
             "gallery": artdir / "gallery.json"}

    print(f"art review for '{args.campaign}'  →  http://{args.host}:{args.port}  "
          f"({'placeholders' if (args.fake or not art.have_token()) else 'live ' + SEED.get('model','')})")
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
