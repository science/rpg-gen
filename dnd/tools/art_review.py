#!/usr/bin/env python3
"""Local web app to review / regenerate / accept Ajiibwan scenario art.

Architecture (single threaded Flask process + a background thread pool):
  - The HTTP layer is thin. POST /api/generate submits a job and returns a
    job-id *immediately*; the ~30s Replicate wait runs in a worker thread
    (art_jobs.JobManager). Because that wait is network-I/O-bound, the GIL is
    released and several subjects generate truly in parallel.
  - The browser owns each card's prompt text (Alpine, no build step) and polls
    GET /api/jobs for live status. No full-page reloads, so an in-flight job can
    never revert another card's edit.

State lives in <campaign>/build/art/gallery.json (gitignored); images saved
alongside it as <id>-tNN.<ext>. Generation goes through tools/art.py, which uses
Replicate when REPLICATE_API_TOKEN is set and offline Pillow placeholders
otherwise (or when ART_FAKE=1).

Run (on the VM; binds 0.0.0.0 so the host browser can reach it):
    .venv/bin/python dnd/tools/art_review.py ajiibwan            # http://<vm-ip>:5005
    .venv/bin/python dnd/tools/art_review.py ajiibwan --port 5005 --fake
"""
from __future__ import annotations

import argparse
import pathlib

import yaml
from flask import (Flask, abort, jsonify, render_template_string, request,
                   send_from_directory)

import art        # sibling module (tools/art.py)
import art_jobs   # sibling module (tools/art_jobs.py)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ASPECT_RATIOS = ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3", "21:9"]


# ------------------------------------------------------------------ app factory
def make_app(campaign_base) -> Flask:
    """Build the Flask app for a campaign folder (…/dnd/<campaign>)."""
    base = pathlib.Path(campaign_base)
    prompts_file = base / "art" / "prompts.yaml"
    seed = yaml.safe_load(prompts_file.read_text()) if prompts_file.is_file() else {}
    artdir = base / "build" / "art"
    artdir.mkdir(parents=True, exist_ok=True)

    app = Flask(__name__)
    app.config["SEED"] = seed
    app.config["MANAGER"] = art_jobs.JobManager(art, artdir)
    app.config.setdefault("FAKE_DELAY", 0.0)  # tests can set this to observe status

    def mgr() -> art_jobs.JobManager:
        return app.config["MANAGER"]

    def state_payload() -> dict:
        st = mgr().get_state(app.config["SEED"])
        subjects = [{"id": sid, **subj} for sid, subj in st["subjects"].items()]
        return {"model": st.get("model", art.DEFAULT_MODEL),
                "size": st.get("size", "2K"), "style": st.get("style", ""),
                "have_token": art.have_token(), "aspect_ratios": ASPECT_RATIOS,
                "subjects": subjects}

    # ---- views --------------------------------------------------------------
    @app.route("/")
    def index():
        return render_template_string(TEMPLATE)

    @app.route("/art/<path:filename>")
    def art_file(filename):
        return send_from_directory(artdir, filename)

    @app.route("/api/state")
    def api_state():
        return jsonify(state_payload())

    @app.route("/api/generate", methods=["POST"])
    def api_generate():
        data = request.get_json(force=True, silent=True) or {}
        sid = data.get("id") or abort(400)
        prompt = (data.get("prompt") or "").strip()
        aspect = data.get("aspect_ratio") or "3:4"
        seed = app.config["SEED"]
        # persist the edit, then kick off the job (returns at once)
        mgr().set_subject(subject_id=sid, prompt=prompt, aspect_ratio=aspect, seed=seed)
        job = mgr().submit_job(
            subject_id=sid, prompt=prompt, aspect_ratio=aspect,
            model=seed.get("model", art.DEFAULT_MODEL),
            size=seed.get("size", "2K"), style=seed.get("style", ""),
            label=sid, delay=app.config["FAKE_DELAY"])
        return jsonify({"job_id": job.id, "n": job.n})

    @app.route("/api/jobs")
    def api_jobs():
        return jsonify({"jobs": mgr().snapshot()})

    @app.route("/api/accept", methods=["POST"])
    def api_accept():
        data = request.get_json(force=True, silent=True) or {}
        sid = data.get("id") or abort(400)
        fname = data.get("file") or abort(400)
        try:
            mgr().accept(subject_id=sid, file=fname, seed=app.config["SEED"])
        except KeyError:
            abort(404)
        return jsonify({"ok": True})

    return app


# ------------------------------------------------------------------- template
TEMPLATE = """
<!doctype html><html><head><meta charset="utf-8"><title>Ajiibwan art review</title>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
<style>
 :root{color-scheme:dark}
 body{background:#16131a;color:#e8e4ee;font:15px/1.45 system-ui,sans-serif;margin:0}
 header{padding:14px 22px;background:#221c2b;border-bottom:1px solid #3a3145;position:sticky;top:0;z-index:5}
 header h1{font-size:18px;margin:0 0 4px}
 .tok{font-size:13px}.ok{color:#7fd18b}.warn{color:#e6c06a}
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:18px;padding:18px 22px}
 .card{background:#1f1b27;border:1px solid #352c42;border-radius:10px;padding:14px}
 .card h3{margin:0 0 8px;font-size:15px}.card h3 small{color:#9a8fae;font-weight:400}
 .cur{width:100%;max-height:420px;object-fit:contain;background:#0d0b11;border-radius:8px;border:1px solid #352c42;display:block}
 .none{display:flex;align-items:center;justify-content:center;color:#6f6680;height:220px;width:100%;background:#0d0b11;border-radius:8px;border:1px solid #352c42}
 .badge{display:inline-block;font-size:11px;padding:1px 7px;border-radius:10px;background:#2e4a32;color:#9be0a6;margin-left:6px}
 .chip{display:inline-block;font-size:11px;padding:1px 8px;border-radius:10px;margin-left:6px}
 .chip.run{background:#2b3a55;color:#a8c4ee}.chip.err{background:#552b2b;color:#eeb0a8}.chip.done{background:#2e4a32;color:#9be0a6}
 textarea{width:100%;box-sizing:border-box;background:#161320;color:#e8e4ee;border:1px solid #3a3145;border-radius:6px;padding:8px;font:13px/1.4 ui-monospace,monospace;resize:vertical;min-height:104px;margin-top:8px}
 .row{display:flex;gap:8px;align-items:center;margin-top:8px;flex-wrap:wrap}
 select,button{background:#2b2336;color:#e8e4ee;border:1px solid #463a55;border-radius:6px;padding:7px 11px;font-size:13px;cursor:pointer}
 button.go{background:#3b2f57;border-color:#5b4a83}button:disabled{opacity:.5;cursor:default}
 button.acc{background:#274a2c;border-color:#3c7044}
 .meta{color:#9a8fae;font-size:12px}
 .film{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}
 .film figure{margin:0;width:84px;text-align:center}
 .film img{width:84px;height:84px;object-fit:cover;border-radius:5px;border:1px solid #352c42;display:block;cursor:pointer}
 .film img.on{border-color:#7fd18b;border-width:2px}
 .film button{padding:2px 6px;font-size:11px;margin-top:3px;width:100%}
 .film figcaption{font-size:10px;color:#9a8fae}
</style></head>
<body x-data="review()" x-init="init()">
<header>
  <h1>Deserts of Ajiibwan — art review</h1>
  <div class="tok">
    <template x-if="have_token"><span class="ok">● live generation (<span x-text="model"></span>, <span x-text="size"></span>)</span></template>
    <template x-if="!have_token"><span class="warn">● no token — offline placeholders (set REPLICATE_API_TOKEN for real images)</span></template>
  </div>
</header>

<div class="grid">
  <template x-for="s in subjects" :key="s.id">
    <div class="card">
      <h3>
        <span x-text="s.label"></span> <small x-text="s.id"></small>
        <template x-if="s.accepted"><span class="badge">accepted</span></template>
        <template x-if="jobFor(s.id)">
          <span class="chip" :class="chipClass(jobFor(s.id))" x-text="jobLabel(jobFor(s.id))"></span>
        </template>
      </h3>

      <template x-if="currentImage(s)">
        <img class="cur" :src="'/art/' + currentImage(s) + '?v=' + bust" :alt="s.id">
      </template>
      <template x-if="!currentImage(s)"><div class="none">no image yet — Generate</div></template>

      <textarea x-model="s.prompt" @input="dirty[s.id]=true"></textarea>
      <div class="row">
        <select x-model="s.aspect_ratio" @change="dirty[s.id]=true">
          <template x-for="ar in aspect_ratios" :key="ar"><option :value="ar" x-text="ar"></option></template>
        </select>
        <button class="go" @click="generate(s)" :disabled="isRunning(s.id)"
                x-text="isRunning(s.id) ? 'generating…' : (have_token ? 'Generate' : 'Generate (placeholder)')"></button>
        <span class="meta"><span x-text="(s.turns||[]).length"></span> turn(s)</span>
      </div>

      <template x-if="(s.turns||[]).length">
        <div class="film">
          <template x-for="t in s.turns" :key="t.file">
            <figure>
              <img :class="t.file==s.accepted ? 'on' : ''" :src="'/art/' + t.file + '?v=' + bust"
                   :title="'turn ' + t.n + ' · ' + t.aspect_ratio">
              <button class="acc" @click="accept(s, t.file)" x-text="t.file==s.accepted ? '✓ accepted' : 'accept'"></button>
              <figcaption x-text="'t' + t.n + ' · ' + t.aspect_ratio + (t.fake ? ' (ph)' : '')"></figcaption>
            </figure>
          </template>
        </div>
      </template>
    </div>
  </template>
</div>

<script>
function review(){
  return {
    model:'', size:'', style:'', have_token:false, aspect_ratios:[],
    subjects:[], jobs:[], bust:0, dirty:{},
    async init(){ await this.loadState(true); setInterval(()=>this.pollJobs(), 1500); },
    async loadState(initial=false){
      const d = await (await fetch('/api/state')).json();
      this.model=d.model; this.size=d.size; this.style=d.style;
      this.have_token=d.have_token; this.aspect_ratios=d.aspect_ratios;
      if(initial){ this.subjects = d.subjects; return; }
      // dirty/clean: the draft fields (prompt, aspect_ratio) are server-hydrated but
      // user-editable. A background refresh re-hydrates a draft ONLY while it's clean.
      // Once you edit it (dirty), we keep your text until the next Generate, which
      // persists your value server-side and marks the draft clean again.
      const byId = Object.fromEntries(this.subjects.map(s=>[s.id,s]));
      this.subjects = d.subjects.map(s=>{
        const cur = byId[s.id];
        if(!cur) return s;                  // brand-new subject — take it wholesale
        if(!this.dirty[s.id]) return s;     // clean — accept server values (incl. prompt)
        return {...s, prompt:cur.prompt, aspect_ratio:cur.aspect_ratio};  // dirty — keep edits
      });
    },
    async generate(s){
      const r = await (await fetch('/api/generate',{method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({id:s.id, prompt:s.prompt, aspect_ratio:s.aspect_ratio})})).json();
      this.dirty[s.id] = false;  // submitted value is now what the server holds → clean
      this.jobs = this.jobs.filter(j=>j.subject_id!==s.id);
      this.jobs.push({id:r.job_id, subject_id:s.id, status:'queued', elapsed:0});
    },
    async accept(s, file){
      await fetch('/api/accept',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({id:s.id, file})});
      s.accepted = file;
    },
    async pollJobs(){
      const d = await (await fetch('/api/jobs')).json();
      const wasRunning = this.subjects.filter(s=>this.isRunning(s.id)).map(s=>s.id);
      this.jobs = d.jobs;
      // when any running job just finished, refresh turns + cache-bust images
      const stillRunning = new Set(this.subjects.filter(s=>this.isRunning(s.id)).map(s=>s.id));
      if(wasRunning.some(id=>!stillRunning.has(id))){ this.bust++; await this.loadState(); }
    },
    jobFor(id){ const js=this.jobs.filter(j=>j.subject_id===id); return js.length?js[js.length-1]:null; },
    isRunning(id){ const j=this.jobFor(id); return !!j && ['queued','starting','processing'].includes(j.status); },
    chipClass(j){ return j.status==='failed'?'err':(j.status==='done'?'done':'run'); },
    jobLabel(j){
      if(j.status==='done') return 'done';
      if(j.status==='failed') return 'failed: ' + (j.error||'');
      return 'generating ' + (j.elapsed||0) + 's';
    },
    currentImage(s){
      if(s.accepted) return s.accepted;
      const t=s.turns||[]; return t.length? t[t.length-1].file : null;
    },
  };
}
</script>
</body></html>
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
    art.load_dotenv(REPO_ROOT / "credentials" / "env.production",
                    REPO_ROOT / ".env", base / ".env")
    if args.fake:
        import os
        os.environ["ART_FAKE"] = "1"

    app = make_app(base)
    live = not (args.fake or not art.have_token())
    print(f"art review for '{args.campaign}'  →  http://{args.host}:{args.port}  "
          f"({'live ' + (app.config['SEED'].get('model','')) if live else 'placeholders'})")
    # threaded=True: status polls/submits are served while a generation runs.
    app.run(host=args.host, port=args.port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
