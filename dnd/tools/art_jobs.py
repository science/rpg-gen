#!/usr/bin/env python3
"""Background job manager + atomic state store for the art review app.

The web layer (`art_review.py`) stays thin: it submits a job and returns
immediately, then polls `snapshot()` for status. The slow work (waiting on
Replicate, ~30s, network-I/O-bound so the GIL is released) runs in a
ThreadPoolExecutor, so several subjects generate in parallel in one process.

All shared state — the in-memory job registry AND the on-disk `gallery.json` —
is mutated only while holding a single `threading.Lock`, and `gallery.json` is
written atomically (temp file + `os.replace`). Together these kill the
read-modify-write race that used to revert a card's prompt edit when another
card was mid-generation.
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import threading
import time
from concurrent.futures import ThreadPoolExecutor


# ------------------------------------------------------------------ state I/O
def _blank_subject(subject_id: str, *, label: str | None = None,
                   aspect_ratio: str = "3:4", prompt: str = "") -> dict:
    return {"label": label or subject_id, "aspect_ratio": aspect_ratio,
            "prompt": prompt, "accepted": None, "turns": []}


def load_state(gallery_path, seed: dict | None = None) -> dict:
    """Read gallery.json (or start empty) and merge top-level config + any new
    subjects from the seed (prompts.yaml). Compatible with the existing schema."""
    gp = pathlib.Path(gallery_path)
    state = json.loads(gp.read_text()) if gp.is_file() else {"subjects": {}}
    state.setdefault("subjects", {})
    if seed:
        state["model"] = seed.get("model", state.get("model", ""))
        state["size"] = seed.get("size", state.get("size", "2K"))
        state["style"] = (seed.get("style") or state.get("style") or "").strip()
        for s in seed.get("subjects", []):
            if s["id"] not in state["subjects"]:
                state["subjects"][s["id"]] = _blank_subject(
                    s["id"], label=s.get("label"),
                    aspect_ratio=s.get("aspect_ratio", "3:4"),
                    prompt=(s.get("prompt") or "").strip())
    return state


def save_state(gallery_path, state: dict) -> None:
    """Atomically persist state (temp file + os.replace). Caller holds the lock."""
    gp = pathlib.Path(gallery_path)
    gp.parent.mkdir(parents=True, exist_ok=True)
    tmp = gp.with_name(f".{gp.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp.write_text(json.dumps(state, indent=2))
    os.replace(tmp, gp)


def effective_prompt(state: dict, subj: dict) -> str:
    """Style preamble + subject prompt (matches the original review-app rule)."""
    style = (state.get("style") or "").strip()
    prompt = subj.get("prompt", "")
    return f"{style}\n\n{prompt}".strip() if style else prompt


# ------------------------------------------------------------------------ Job
@dataclasses.dataclass
class Job:
    id: str
    subject_id: str
    prompt: str
    aspect_ratio: str
    model: str = ""
    n: int = 0
    status: str = "queued"   # queued | starting | processing | done | failed
    started_at: float | None = None
    finished_at: float | None = None
    error: str | None = None
    file: str | None = None
    fake: bool = False

    def to_dict(self, now: float) -> dict:
        if self.started_at is None:
            elapsed = 0.0
        else:
            elapsed = round((self.finished_at or now) - self.started_at, 1)
        return {"id": self.id, "subject_id": self.subject_id, "n": self.n,
                "status": self.status, "elapsed": elapsed, "error": self.error,
                "file": self.file, "aspect_ratio": self.aspect_ratio,
                "model": self.model, "fake": self.fake}


# ----------------------------------------------------------------- JobManager
class JobManager:
    def __init__(self, art_module, artdir, *, gallery_path=None, executor=None,
                 max_workers: int = 4, poll_interval: float = 0.25,
                 time_fn=time.time):
        self.art = art_module
        self.artdir = pathlib.Path(artdir)
        self.gallery_path = pathlib.Path(gallery_path or self.artdir / "gallery.json")
        self.executor = executor or ThreadPoolExecutor(max_workers=max_workers)
        self.poll_interval = poll_interval
        self.time = time_fn
        self.lock = threading.Lock()
        self.jobs: dict[str, Job] = {}
        self._seq = 0

    # -- state mutations (all behind the lock) ----------------------------
    def get_state(self, seed: dict | None = None) -> dict:
        with self.lock:
            return load_state(self.gallery_path, seed)

    def set_subject(self, *, subject_id: str, prompt: str | None = None,
                    aspect_ratio: str | None = None, model: str | None = None,
                    seed: dict | None = None) -> dict:
        with self.lock:
            state = load_state(self.gallery_path, seed)
            subj = state["subjects"].setdefault(subject_id, _blank_subject(subject_id))
            if prompt is not None:
                subj["prompt"] = prompt
            if aspect_ratio is not None:
                subj["aspect_ratio"] = aspect_ratio
            if model is not None:
                subj["model"] = model
            save_state(self.gallery_path, state)
            return subj

    def accept(self, *, subject_id: str, file: str, seed: dict | None = None) -> dict:
        with self.lock:
            state = load_state(self.gallery_path, seed)
            subj = state["subjects"].get(subject_id)
            if subj is None:
                raise KeyError(subject_id)
            subj["accepted"] = file
            save_state(self.gallery_path, state)
            return subj

    # -- jobs --------------------------------------------------------------
    def submit_job(self, *, subject_id: str, prompt: str, aspect_ratio: str,
                   model: str, size: str, style: str = "", label: str = "",
                   fake: bool | None = None, delay: float = 0.0,
                   reference_images: list[str] | None = None) -> Job:
        with self.lock:
            self._seq += 1
            jid = f"job{self._seq}"
            job = Job(id=jid, subject_id=subject_id, prompt=prompt,
                      aspect_ratio=aspect_ratio, model=model,
                      fake=self.art._is_fake(fake, self.art.provider_for(model)))
            self.jobs[jid] = job
        self.executor.submit(self._run, job, model, size, style, label, fake, delay,
                             reference_images)
        return job

    def get_job(self, job_id: str) -> Job:
        with self.lock:
            return self.jobs[job_id]

    def snapshot(self, now: float | None = None) -> list[dict]:
        now = self.time() if now is None else now
        with self.lock:
            return [j.to_dict(now) for j in self.jobs.values()]

    # -- worker ------------------------------------------------------------
    def _run(self, job: Job, model, size, style, label, fake, delay,
             reference_images=None):
        with self.lock:
            job.status = "starting"
            job.started_at = self.time()
        try:
            eff = self._effective_prompt(style, job.prompt)
            handle = self.art.submit(eff, model=model, aspect_ratio=job.aspect_ratio,
                                     size=size, label=label, fake=fake, delay=delay,
                                     reference_images=reference_images)
            while True:
                r = self.art.poll(handle)
                status = r["status"]
                if status == "succeeded":
                    fname = self._record_turn(job, r["output_bytes"], r["ext"] or "png")
                    with self.lock:
                        job.file = fname
                        job.status = "done"
                        job.finished_at = self.time()
                    return
                if status in ("failed", "canceled"):
                    with self.lock:
                        job.status = "failed"
                        job.error = r.get("error") or status
                        job.finished_at = self.time()
                    return
                with self.lock:
                    job.status = "processing"
                time.sleep(self.poll_interval)
        except Exception as e:  # noqa: BLE001 — record, don't crash the worker
            with self.lock:
                job.status = "failed"
                job.error = str(e)
                job.finished_at = self.time()

    def _effective_prompt(self, style: str, prompt: str) -> str:
        style = (style or "").strip()
        return f"{style}\n\n{prompt}".strip() if style else prompt

    def _record_turn(self, job: Job, data: bytes, ext: str) -> str:
        """Reserve the next turn number, write the image atomically, append the
        turn to gallery.json — all under the lock so nothing clobbers it."""
        with self.lock:
            state = load_state(self.gallery_path)
            subj = state["subjects"].setdefault(
                job.subject_id, _blank_subject(job.subject_id, prompt=job.prompt,
                                               aspect_ratio=job.aspect_ratio))
            n = len(subj["turns"]) + 1
            fname = f"{job.subject_id}-t{n:02d}.{ext}"
            self.artdir.mkdir(parents=True, exist_ok=True)
            tmp = self.artdir / f".{fname}.tmp"
            tmp.write_bytes(data)
            os.replace(tmp, self.artdir / fname)
            subj["turns"].append({"n": n, "file": fname, "prompt": job.prompt,
                                  "aspect_ratio": job.aspect_ratio,
                                  "model": job.model, "fake": job.fake})
            job.n = n
            save_state(self.gallery_path, state)
        return fname
