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
        default_model = st.get("model", art.DEFAULT_MODEL)
        subjects = []
        for sid, subj in st["subjects"].items():
            subjects.append({"id": sid, **subj,
                             "model": subj.get("model") or default_model})
        return {"model": default_model,
                "size": st.get("size", "2K"), "style": st.get("style", ""),
                "have_token": art.have_token(), "aspect_ratios": ASPECT_RATIOS,
                "models": art.MODEL_REGISTRY, "subjects": subjects}

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
        model = data.get("model") or seed.get("model", art.DEFAULT_MODEL)
        # resolve an optional "adjust from" source image to a local path (image-to-image)
        refs = None
        adjust_from = data.get("adjust_from")
        if adjust_from:
            src = artdir / pathlib.Path(adjust_from).name  # basename only — no traversal
            if src.is_file():
                refs = [str(src)]
        # persist the edits, then kick off the job (returns at once)
        mgr().set_subject(subject_id=sid, prompt=prompt, aspect_ratio=aspect,
                          model=model, seed=seed)
        job = mgr().submit_job(
            subject_id=sid, prompt=prompt, aspect_ratio=aspect, model=model,
            size=seed.get("size", "2K"), style=seed.get("style", ""),
            label=sid, delay=app.config["FAKE_DELAY"], reference_images=refs)
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
            subj = mgr().accept(subject_id=sid, file=fname, seed=app.config["SEED"])
        except KeyError:
            abort(404)
        # echo the (possibly toggled-off) selection so the UI reflects the server
        return jsonify({"ok": True, "accepted": subj["accepted"]})

    @app.route("/api/add_subject", methods=["POST"])
    def api_add_subject():
        data = request.get_json(force=True, silent=True) or {}
        label = (data.get("label") or "").strip()
        aspect = data.get("aspect_ratio") or "3:4"
        sid, subj = mgr().add_subject(label=label, aspect_ratio=aspect)
        return jsonify({"id": sid, **subj})

    @app.route("/api/delete", methods=["POST"])
    def api_delete():
        data = request.get_json(force=True, silent=True) or {}
        sid = data.get("id") or abort(400)
        mgr().delete_subject(sid)
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
 .cur{cursor:zoom-in}
 label.adj{display:flex;align-items:center;gap:5px;font-size:12px;color:#cabfe0;cursor:pointer}
 label.adj input{cursor:pointer}
 button.del{background:#2b2336;border-color:#5a3a3a;color:#e6a8a8;padding:5px 9px}
 button.del:hover{background:#3a2b2b}
 .card.add{display:flex;flex-direction:column;justify-content:center;align-items:stretch;border-style:dashed;border-color:#4a3f59;background:#1a1622}
 .card.add h3{text-align:center;color:#cabfe0}
 .card.add input{width:100%;box-sizing:border-box;background:#161320;color:#e8e4ee;border:1px solid #3a3145;border-radius:6px;padding:8px;font-size:13px;margin-bottom:8px}
 /* lightbox */
 .lb{position:fixed;inset:0;background:rgba(8,6,12,.92);z-index:50;display:flex;flex-direction:column;align-items:center;justify-content:center}
 .lb img{max-width:92vw;max-height:80vh;object-fit:contain;border-radius:6px;box-shadow:0 10px 40px #000}
 .lb .x{position:absolute;top:16px;right:20px;font-size:22px;line-height:1;padding:6px 12px}
 .lb .nav{position:absolute;top:50%;transform:translateY(-50%);font-size:30px;padding:10px 16px;background:#2b2336cc;border-color:#5b4a83}
 .lb .nav.l{left:18px}.lb .nav.r{right:18px}
 .lb .cap{margin-top:14px;display:flex;gap:14px;align-items:center;background:#1f1b27cc;border:1px solid #352c42;border-radius:8px;padding:8px 14px;max-width:92vw}
 .lb .cap .t{font-size:13px;color:#e8e4ee}
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
        <img class="cur" :src="'/art/' + currentImage(s) + '?v=' + bust" :alt="s.id"
             @click="openLightbox(currentImage(s))">
      </template>
      <template x-if="!currentImage(s)"><div class="none">no image yet — Generate</div></template>

      <textarea x-model="s.prompt" @input="dirty[s.id]=true"></textarea>
      <div class="row">
        <select x-model="s.model" @change="dirty[s.id]=true" title="model">
          <template x-for="m in models" :key="m.id"><option :value="m.id" x-text="m.label"></option></template>
        </select>
        <select x-model="s.aspect_ratio" @change="dirty[s.id]=true" title="aspect ratio">
          <template x-for="ar in aspect_ratios" :key="ar"><option :value="ar" x-text="ar"></option></template>
        </select>
      </div>
      <div class="row">
        <button class="go" @click="generate(s)" :disabled="isRunning(s.id)"
                x-text="isRunning(s.id) ? 'generating…' : (have_token ? 'Generate' : 'Generate (placeholder)')"></button>
        <template x-if="currentImage(s) && modelMeta(s.model).i2i">
          <label class="adj" :title="'use the current image as input — ' + modelMeta(s.model).label">
            <input type="checkbox" x-model="adjust[s.id]"> adjust from current
          </label>
        </template>
        <span class="meta"><span x-text="(s.turns||[]).length"></span> turn(s)</span>
        <button class="del" @click="del(s)" title="delete this box and its images">🗑 delete</button>
      </div>

      <template x-if="(s.turns||[]).length">
        <div class="film">
          <template x-for="t in s.turns" :key="t.file">
            <figure>
              <img :class="t.file==s.accepted ? 'on' : ''" :src="'/art/' + t.file + '?v=' + bust"
                   :title="'turn ' + t.n + ' · ' + t.aspect_ratio" @click="openLightbox(t.file)">
              <button class="acc" @click="accept(s, t.file)" x-text="t.file==s.accepted ? '✓ accepted' : 'accept'"></button>
              <figcaption x-text="'t' + t.n + ' · ' + t.aspect_ratio + (t.fake ? ' (ph)' : '')"></figcaption>
            </figure>
          </template>
        </div>
      </template>
    </div>
  </template>

  <!-- add a fresh general-purpose box to generate & iterate on any image -->
  <div class="card add">
    <h3>+ New box</h3>
    <input x-model="newLabel" placeholder="Label (optional)" @keydown.enter="addBox()">
    <div class="row"><button class="go" @click="addBox()">Add box</button></div>
    <div class="meta">A blank canvas — name it, write a prompt, pick a model, generate.</div>
  </div>
</div>

<!-- lightbox: global gallery across all images -->
<template x-if="lightbox.open && lbCur()">
  <div class="lb" @keydown.window.escape="lbClose()"
       @keydown.window.arrow-left="lbNav(-1)" @keydown.window.arrow-right="lbNav(1)">
    <button class="x" @click="lbClose()" title="close (Esc)">✕</button>
    <button class="nav l" @click="lbNav(-1)" title="previous (←)">‹</button>
    <img :src="'/art/' + lbCur().file + '?v=' + bust" :alt="lbCur().subjectId">
    <button class="nav r" @click="lbNav(1)" title="next (→)">›</button>
    <div class="cap">
      <span class="t" x-text="lbCur().label + ' · t' + lbCur().n + ' · ' + lbCur().aspect + ' · ' + modelLabel(lbCur().model)"></span>
      <button class="acc" @click="lbAccept()"
              x-text="lbIsAccepted() ? '✓ accepted' : 'accept'"></button>
    </div>
  </div>
</template>

<script>
function review(){
  return {
    model:'', size:'', style:'', have_token:false, aspect_ratios:[], models:[],
    subjects:[], jobs:[], bust:0, dirty:{}, adjust:{}, newLabel:'', lightbox:{open:false,index:0},
    async init(){ await this.loadState(true); setInterval(()=>this.pollJobs(), 1500); },
    async loadState(initial=false){
      const d = await (await fetch('/api/state')).json();
      this.model=d.model; this.size=d.size; this.style=d.style;
      this.have_token=d.have_token; this.aspect_ratios=d.aspect_ratios;
      this.models=d.models||[];
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
        return {...s, prompt:cur.prompt, aspect_ratio:cur.aspect_ratio, model:cur.model};  // dirty — keep edits
      });
    },
    async generate(s){
      const body = {id:s.id, prompt:s.prompt, aspect_ratio:s.aspect_ratio, model:s.model};
      if(this.adjust[s.id] && this.currentImage(s)) body.adjust_from = this.currentImage(s);
      const r = await (await fetch('/api/generate',{method:'POST',
        headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)})).json();
      this.dirty[s.id] = false;  // submitted value is now what the server holds → clean
      this.jobs = this.jobs.filter(j=>j.subject_id!==s.id);
      this.jobs.push({id:r.job_id, subject_id:s.id, status:'queued', elapsed:0});
    },
    async addBox(){
      const r = await (await fetch('/api/add_subject',{method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({label:this.newLabel})})).json();
      this.newLabel='';
      this.subjects.push({id:r.id, label:r.label, aspect_ratio:r.aspect_ratio,
        prompt:r.prompt, accepted:r.accepted, turns:r.turns||[], model:this.model});
    },
    async del(s){
      if(!confirm('Remove the box "'+(s.label||s.id)+'"? (its image files are kept on disk)')) return;
      await fetch('/api/delete',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({id:s.id})});
      this.subjects = this.subjects.filter(x=>x.id!==s.id);
      this.jobs = this.jobs.filter(j=>j.subject_id!==s.id);
      if(this.lightbox.open) this.lbClose();
    },
    modelMeta(id){ return this.models.find(m=>m.id===id) || {id, label:id, i2i:false}; },
    modelLabel(id){ return id ? this.modelMeta(id).label : '—'; },
    allImages(){
      const out=[];
      for(const s of this.subjects){ for(const t of (s.turns||[])){
        out.push({subjectId:s.id, label:s.label, file:t.file, n:t.n,
                  aspect:t.aspect_ratio, model:t.model});
      }}
      return out;
    },
    openLightbox(file){
      const i=this.allImages().findIndex(im=>im.file===file);
      if(i>=0){ this.lightbox.index=i; this.lightbox.open=true; }
    },
    lbCur(){ const a=this.allImages(); return a.length? a[Math.min(this.lightbox.index,a.length-1)] : null; },
    lbNav(d){ const a=this.allImages(); if(!a.length) return; this.lightbox.index=(this.lightbox.index+d+a.length)%a.length; },
    lbClose(){ this.lightbox.open=false; },
    lbSubject(){ const im=this.lbCur(); return im? this.subjects.find(s=>s.id===im.subjectId) : null; },
    lbIsAccepted(){ const im=this.lbCur(), s=this.lbSubject(); return !!im && !!s && s.accepted===im.file; },
    lbAccept(){ const im=this.lbCur(), s=this.lbSubject(); if(im && s) this.accept(s, im.file); },
    async accept(s, file){
      // server toggles: accepting the already-accepted image clears it (none selected)
      const r = await (await fetch('/api/accept',{method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({id:s.id, file})})).json();
      s.accepted = r.accepted;
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
