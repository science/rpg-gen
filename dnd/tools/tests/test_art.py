"""Unit tests for the art.py Replicate layer (submit / poll / helpers).

Key regression: the aspect ratio the user picks must reach the model payload
(UAT bug #3 was actually a display crop, but we pin the payload here so a real
regression can't slip in).
"""
import art
from conftest import PNG_1x1


# --------------------------------------------------------------- payload (#3)
def test_build_payload_carries_prompt_aspect_size():
    p = art._build_payload("a tower", aspect_ratio="16:9", size="3K")
    assert p["prompt"] == "a tower"
    assert p["aspect_ratio"] == "16:9"
    assert p["size"] == "3K"
    assert "image_input" not in p  # omitted when no refs


def test_build_payload_includes_reference_images_when_given():
    p = art._build_payload("x", aspect_ratio="1:1", size="2K",
                           reference_images=["http://example/a.png"])
    assert p["image_input"] == ["http://example/a.png"]


class _FakeCreate:
    """Captures the input dict passed to predictions.create()."""
    def __init__(self, prediction):
        self.prediction = prediction
        self.captured = None

    def __call__(self, *, model=None, input=None, **kw):
        self.captured = {"model": model, "input": input}
        return self.prediction


class _FakePrediction:
    def __init__(self, status="succeeded", output=None, logs="", error=None):
        self.status = status
        self.output = output
        self.logs = logs
        self.error = error
        self.reloaded = 0

    def reload(self):
        self.reloaded += 1


class _FakeClient:
    def __init__(self, prediction):
        self.predictions = type("P", (), {})()
        self.predictions.create = _FakeCreate(prediction)


def test_submit_live_sends_chosen_aspect_ratio_to_client():
    pred = _FakePrediction(status="succeeded", output=[PNG_1x1])
    client = _FakeClient(pred)
    handle = art.submit("a tower", model="bytedance/seedream-5-lite",
                        aspect_ratio="16:9", size="2K", fake=False, client=client)
    captured = client.predictions.create.captured
    assert captured["model"] == "bytedance/seedream-5-lite"
    assert captured["input"]["aspect_ratio"] == "16:9"   # <- the #3 guard
    # And polling that handle yields the image bytes.
    r = art.poll(handle)
    assert r["status"] == "succeeded"
    assert r["output_bytes"] == PNG_1x1
    assert r["ext"] == "png"


def test_poll_live_surfaces_processing_then_error():
    pred = _FakePrediction(status="processing")
    client = _FakeClient(pred)
    handle = art.submit("x", aspect_ratio="3:4", size="2K", fake=False, client=client)
    r = art.poll(handle)
    assert r["status"] == "processing"
    assert r["output_bytes"] is None
    # flip to a failure and re-poll
    pred.status, pred.error = "failed", "NSFW content"
    r = art.poll(handle)
    assert r["status"] == "failed"
    assert "NSFW" in (r["error"] or "")


# --------------------------------------------------------------- byte helpers
def test_ext_from_bytes_detects_formats():
    assert art._ext_from_bytes(PNG_1x1) == "png"
    assert art._ext_from_bytes(b"\xff\xd8\xff\xe0blah") == "jpg"
    assert art._ext_from_bytes(b"RIFF\x00\x00\x00\x00WEBPVP8 ") == "webp"


def test_read_output_handles_list_bytes_and_fileoutput():
    assert art._read_output([PNG_1x1]) == PNG_1x1
    assert art._read_output(PNG_1x1) == PNG_1x1

    class _FileOut:
        def read(self):
            return PNG_1x1
    assert art._read_output([_FileOut()]) == PNG_1x1


# --------------------------------------------------------------- fake handle
def test_fake_submit_poll_reaches_succeeded_with_png():
    handle = art.submit("a tower", aspect_ratio="16:9", fake=True, delay=0.0,
                        label="tower")
    r = art.poll(handle)
    assert r["status"] == "succeeded"
    assert art._ext_from_bytes(r["output_bytes"]) == "png"


def test_fake_handle_progresses_over_delay():
    handle = art.submit("x", aspect_ratio="3:4", fake=True, delay=0.5)
    first = art.poll(handle)
    assert first["status"] in ("starting", "processing")
    assert first["output_bytes"] is None
    import time
    time.sleep(0.6)
    done = art.poll(handle)
    assert done["status"] == "succeeded"
    assert done["output_bytes"] is not None
