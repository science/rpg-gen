# Adventure Scripts

> Part of the [Cthulhu-Gen](../README.md) monorepo. **Planned — not yet built.**

A tool for **creating and improving adventure scripts / scenarios** for *Call
of Cthulhu*: drafting new ones, restructuring existing ones, and revising them
for pacing, clarity, and playability.

## Intent (to be refined)

- Take an adventure in some input form (rough notes, an existing scenario doc, a
  YAML/Markdown outline) and **produce or update** a structured script.
- "Improve" passes: tighten pacing, surface plot holes and dead ends, balance
  clue distribution, flag missing handouts/NPCs/locations, suggest hooks.
- Output in a readable, runnable-at-the-table format (and, like
  `character-sheets/`, a print-friendly rendering down the line).

## Conventions to follow

This folder will be self-contained like the other tools:

- its own `requirements.txt`, installed into the repo-root `../.venv`;
- paths resolved relative to the tool's own entry point;
- generated output under `build/` (git-ignored);
- reusable helpers promoted to [`../shared/`](../shared/) only once a second
  tool needs them.

_This README is a placeholder; the design lands when the tool is built._
