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


# ============================================================ model registry
def test_registry_lists_three_models_with_providers():
    ids = {m["id"] for m in art.MODEL_REGISTRY}
    assert "bytedance/seedream-5-lite" in ids
    assert "bytedance/seedream-4.5" in ids
    assert "gpt-image-2" in ids


def test_provider_for_routes_by_model():
    assert art.provider_for("bytedance/seedream-5-lite") == "replicate"
    assert art.provider_for("bytedance/seedream-4.5") == "replicate"
    assert art.provider_for("gpt-image-2") == "openai"
    assert art.provider_for("something-unknown") == "replicate"  # safe fallback


def test_model_meta_reports_i2i_support():
    assert art.model_meta("gpt-image-2")["i2i"] is True
    assert art.model_meta("bytedance/seedream-4.5")["i2i"] is True


def test_have_token_for_provider(monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "x")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert art.have_token_for("replicate") is True
    assert art.have_token_for("openai") is False
    monkeypatch.setenv("OPENAI_API_KEY", "y")
    assert art.have_token_for("openai") is True


def test_aspect_to_openai_size_mapping():
    assert art._aspect_to_openai_size("16:9") == "1536x1024"   # landscape
    assert art._aspect_to_openai_size("3:2") == "1536x1024"
    assert art._aspect_to_openai_size("9:16") == "1024x1536"   # portrait
    assert art._aspect_to_openai_size("3:4") == "1024x1536"
    assert art._aspect_to_openai_size("1:1") == "1024x1024"    # square


# -------------------------------------------------- replicate image-to-image
def test_replicate_reference_image_becomes_data_uri(tmp_path):
    ref = tmp_path / "src.png"
    ref.write_bytes(PNG_1x1)
    pred = _FakePrediction(status="succeeded", output=[PNG_1x1])
    client = _FakeClient(pred)
    art.submit("tweak it", model="bytedance/seedream-4.5", aspect_ratio="1:1",
               size="2K", reference_images=[str(ref)], fake=False, client=client)
    img_in = client.predictions.create.captured["input"]["image_input"]
    assert isinstance(img_in, list) and len(img_in) == 1
    assert img_in[0].startswith("data:image/png;base64,")


# ----------------------------------------------------------- openai provider
import base64


def _b64(data):
    return base64.b64encode(data).decode()


class _FakeImages:
    def __init__(self, b64):
        self._b64 = b64
        self.gen_captured = None
        self.edit_captured = None

    def _resp(self):
        return type("R", (), {"data": [type("D", (), {"b64_json": self._b64})()]})()

    def generate(self, **kw):
        self.gen_captured = kw
        return self._resp()

    def edit(self, **kw):
        self.edit_captured = kw
        return self._resp()


class _FakeOpenAI:
    def __init__(self, b64):
        self.images = _FakeImages(b64)


def _drain(handle, timeout=3.0):
    import time
    end = time.time() + timeout
    while time.time() < end:
        r = art.poll(handle)
        if r["status"] in ("succeeded", "failed"):
            return r
        time.sleep(0.02)
    raise AssertionError(f"openai handle stuck at {r['status']}")


def test_openai_generate_maps_size_and_decodes_b64():
    client = _FakeOpenAI(_b64(PNG_1x1))
    handle = art.submit("a tower", model="gpt-image-2", aspect_ratio="16:9",
                        fake=False, client=client)
    r = _drain(handle)
    assert r["status"] == "succeeded"
    assert r["output_bytes"] == PNG_1x1
    assert client.images.generate.__self__.gen_captured["model"] == "gpt-image-2"
    assert client.images.generate.__self__.gen_captured["size"] == "1536x1024"
    assert client.images.edit.__self__.edit_captured is None  # generate, not edit


def test_openai_edit_path_used_when_reference_given(tmp_path):
    ref = tmp_path / "src.png"
    ref.write_bytes(PNG_1x1)
    client = _FakeOpenAI(_b64(PNG_1x1))
    handle = art.submit("make it night", model="gpt-image-2", aspect_ratio="1:1",
                        reference_images=[str(ref)], fake=False, client=client)
    r = _drain(handle)
    assert r["status"] == "succeeded"
    cap = client.images.edit.__self__.edit_captured
    assert cap is not None and isinstance(cap["image"], list) and len(cap["image"]) == 1
    assert client.images.generate.__self__.gen_captured is None  # edit, not generate
