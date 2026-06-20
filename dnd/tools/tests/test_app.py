"""Tests for the art_review Flask JSON API (no full-page reloads anymore).

Verifies the request layer stays thin: generate returns a job id immediately
(work happens in the background), prompt edits sent on generate are persisted,
and accept records the chosen file.
"""
import time

import pytest
import yaml

import art_review


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("ART_FAKE", "1")  # offline placeholders, no network
    base = tmp_path / "ajiibwan"
    (base / "art").mkdir(parents=True)
    (base / "art" / "prompts.yaml").write_text(yaml.safe_dump({
        "model": "bytedance/seedream-5-lite",
        "size": "2K",
        "style": "test style",
        "subjects": [
            {"id": "alpha", "label": "Alpha", "aspect_ratio": "3:4", "prompt": "prompt A"},
            {"id": "beta", "label": "Beta", "aspect_ratio": "16:9", "prompt": "prompt B"},
        ],
    }))
    application = art_review.make_app(base)
    application.config["FAKE_DELAY"] = 0.4  # let us observe in-flight status
    application.config["TESTING"] = True
    return application


def test_state_lists_seed_subjects(app):
    c = app.test_client()
    state = c.get("/api/state").get_json()
    ids = {s["id"] for s in state["subjects"]}
    assert ids == {"alpha", "beta"}
    assert state["style"] == "test style"


def test_generate_returns_job_id_without_blocking(app):
    c = app.test_client()
    t0 = time.time()
    resp = c.post("/api/generate", json={"id": "alpha", "prompt": "prompt A",
                                         "aspect_ratio": "16:9"})
    dt = time.time() - t0
    body = resp.get_json()
    assert resp.status_code == 200
    assert body["job_id"]
    # returned well before the 0.4s generation could possibly finish
    assert dt < 0.3
    # and the job is observably in flight right after submit
    jobs = c.get("/api/jobs").get_json()["jobs"]
    row = next(j for j in jobs if j["id"] == body["job_id"])
    assert row["status"] in ("queued", "starting", "processing")
    # it completes on its own
    end = time.time() + 5
    while time.time() < end:
        jobs = c.get("/api/jobs").get_json()["jobs"]
        row = next(j for j in jobs if j["id"] == body["job_id"])
        if row["status"] == "done":
            break
        time.sleep(0.05)
    assert row["status"] == "done"


def test_prompt_edit_sent_on_generate_is_persisted(app):
    c = app.test_client()
    c.post("/api/generate", json={"id": "alpha", "prompt": "A BRAND NEW PROMPT",
                                  "aspect_ratio": "3:4"})
    state = c.get("/api/state").get_json()
    alpha = next(s for s in state["subjects"] if s["id"] == "alpha")
    assert alpha["prompt"] == "A BRAND NEW PROMPT"


def test_accept_sets_accepted_file(app):
    c = app.test_client()
    body = c.post("/api/generate", json={"id": "beta", "prompt": "prompt B",
                                         "aspect_ratio": "16:9"}).get_json()
    # wait for completion to learn the produced filename
    end = time.time() + 5
    fname = None
    while time.time() < end:
        jobs = c.get("/api/jobs").get_json()["jobs"]
        row = next(j for j in jobs if j["id"] == body["job_id"])
        if row["status"] == "done":
            fname = row["file"]
            break
        time.sleep(0.05)
    assert fname
    r = c.post("/api/accept", json={"id": "beta", "file": fname})
    assert r.status_code == 200
    state = c.get("/api/state").get_json()
    beta = next(s for s in state["subjects"] if s["id"] == "beta")
    assert beta["accepted"] == fname


def test_index_serves_html_shell(app):
    c = app.test_client()
    html = c.get("/").get_data(as_text=True)
    assert "<html" in html.lower()
    assert "alpine" in html.lower() or "x-data" in html.lower()
