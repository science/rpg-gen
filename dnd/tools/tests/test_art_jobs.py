"""Tests for art_jobs.JobManager + the atomic, locked state store.

These pin the two architectural fixes:
  - concurrent generations actually run in parallel and both persist (#2 concurrency)
  - an in-flight job never clobbers another card's prompt edit (#2 the revert bug)
  - job status is observable, including the error path (#1 progress data source)
  - gallery.json writes are atomic under concurrent writers
"""
import json
import threading
import time

import art
import art_jobs


# ------------------------------------------------------------------ helpers
def _make_manager(tmp_path):
    artdir = tmp_path / "build" / "art"
    artdir.mkdir(parents=True)
    return art_jobs.JobManager(art, artdir, max_workers=4, poll_interval=0.02)


def _wait(mgr, job, timeout=5.0):
    end = time.time() + timeout
    while time.time() < end:
        cur = mgr.get_job(job.id)
        if cur.status in ("done", "failed"):
            return cur
        time.sleep(0.02)
    raise AssertionError(f"job {job.id} stuck at {mgr.get_job(job.id).status}")


def _gen_kwargs(subject_id, prompt, aspect="3:4", **extra):
    base = dict(subject_id=subject_id, prompt=prompt, aspect_ratio=aspect,
                model="bytedance/seedream-5-lite", size="2K", style="", fake=True)
    base.update(extra)
    return base


# ------------------------------------------------------------ state store
def test_load_state_reads_existing_gallery_schema(tmp_path):
    artdir = tmp_path / "build" / "art"
    artdir.mkdir(parents=True)
    gp = artdir / "gallery.json"
    gp.write_text(json.dumps({"subjects": {
        "tower": {"label": "Tower", "aspect_ratio": "16:9", "prompt": "p",
                  "accepted": None, "turns": [{"n": 1, "file": "tower-t01.png",
                  "prompt": "p", "aspect_ratio": "16:9", "fake": False}]}}}))
    state = art_jobs.load_state(gp)
    assert state["subjects"]["tower"]["turns"][0]["file"] == "tower-t01.png"


def test_save_state_is_atomic_under_concurrent_writers(tmp_path):
    mgr = _make_manager(tmp_path)
    threads = [threading.Thread(target=mgr.set_subject,
                                kwargs={"subject_id": f"s{i}", "prompt": f"p{i}"})
               for i in range(12)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    state = mgr.get_state()
    # valid JSON on disk and every writer's key survived
    json.loads((mgr.gallery_path).read_text())
    for i in range(12):
        assert state["subjects"][f"s{i}"]["prompt"] == f"p{i}"


# ----------------------------------------------------------- concurrency #2
def test_two_subjects_generate_concurrently_and_both_persist(tmp_path):
    mgr = _make_manager(tmp_path)
    a = mgr.submit_job(**_gen_kwargs("alpha", "prompt A", delay=0.3))
    b = mgr.submit_job(**_gen_kwargs("beta", "prompt B", delay=0.3))
    t0 = time.time()
    _wait(mgr, a)
    _wait(mgr, b)
    wall = time.time() - t0
    # ran in parallel: two 0.3s jobs finish well under their 0.6s serial sum
    assert wall < 0.55
    state = mgr.get_state()
    assert len(state["subjects"]["alpha"]["turns"]) == 1
    assert len(state["subjects"]["beta"]["turns"]) == 1
    for sid in ("alpha", "beta"):
        f = state["subjects"][sid]["turns"][0]["file"]
        assert (mgr.artdir / f).is_file()


def test_inflight_job_does_not_clobber_a_prompt_edit(tmp_path):
    mgr = _make_manager(tmp_path)
    # seed subject alpha with an original prompt
    mgr.set_subject(subject_id="alpha", prompt="original A")
    # start a slow generation for beta
    b = mgr.submit_job(**_gen_kwargs("beta", "prompt B", delay=0.4))
    # while beta is in flight, edit alpha's prompt (the action that used to revert)
    time.sleep(0.1)
    mgr.set_subject(subject_id="alpha", prompt="EDITED A")
    _wait(mgr, b)
    state = mgr.get_state()
    assert state["subjects"]["alpha"]["prompt"] == "EDITED A"   # not reverted
    assert len(state["subjects"]["beta"]["turns"]) == 1          # and B persisted


# -------------------------------------------------------------- status #1
def test_job_status_lifecycle_success(tmp_path):
    mgr = _make_manager(tmp_path)
    job = mgr.submit_job(**_gen_kwargs("alpha", "p", delay=0.3))
    # observe it as not-yet-done shortly after submit
    time.sleep(0.05)
    assert mgr.get_job(job.id).status in ("queued", "starting", "processing")
    done = _wait(mgr, job)
    assert done.status == "done"
    assert done.file and (mgr.artdir / done.file).is_file()
    assert done.finished_at and done.started_at


def test_job_records_error_on_failure(tmp_path, monkeypatch):
    mgr = _make_manager(tmp_path)

    def boom(*a, **k):
        raise RuntimeError("replicate exploded")
    monkeypatch.setattr(art, "submit", boom)

    job = mgr.submit_job(**_gen_kwargs("alpha", "p"))
    done = _wait(mgr, job)
    assert done.status == "failed"
    assert "exploded" in (done.error or "")


def test_turn_records_the_model_used(tmp_path):
    mgr = _make_manager(tmp_path)
    job = mgr.submit_job(**_gen_kwargs("alpha", "p", model="bytedance/seedream-4.5"))
    _wait(mgr, job)
    turn = mgr.get_state()["subjects"]["alpha"]["turns"][0]
    assert turn["model"] == "bytedance/seedream-4.5"


def test_reference_images_flow_through_to_art_submit(tmp_path, monkeypatch):
    mgr = _make_manager(tmp_path)
    captured = {}
    orig = art.submit

    def spy(*a, **k):
        captured.update(k)
        return orig(*a, **k)
    monkeypatch.setattr(art, "submit", spy)

    job = mgr.submit_job(**_gen_kwargs("alpha", "adjust", reference_images=["/tmp/x.png"]))
    _wait(mgr, job)
    assert captured.get("reference_images") == ["/tmp/x.png"]
    assert len(mgr.get_state()["subjects"]["alpha"]["turns"]) == 1


def test_snapshot_is_json_serializable(tmp_path):
    mgr = _make_manager(tmp_path)
    job = mgr.submit_job(**_gen_kwargs("alpha", "p", delay=0.2))
    _wait(mgr, job)
    snap = mgr.snapshot()
    json.dumps(snap)  # must not raise
    row = next(r for r in snap if r["id"] == job.id)
    assert row["subject_id"] == "alpha"
    assert row["status"] == "done"
    assert row["elapsed"] >= 0
