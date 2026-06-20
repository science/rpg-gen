"""Pytest setup for the art tooling tests.

Puts the sibling ``tools/`` directory on ``sys.path`` so ``import art``,
``import art_jobs`` and ``import art_review`` resolve when tests run from
anywhere (e.g. ``pytest dnd/tools/tests``).
"""
import pathlib
import sys

TOOLS = pathlib.Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

# A 1x1 PNG (valid signature) used as fake model output in tests.
PNG_1x1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)
