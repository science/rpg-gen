# Adventure Scripts

> A *Call of Cthulhu* tool in the [rpg-gen](../../README.md) monorepo (see the
> [Cthulhu game index](../README.md)). **Planned — not yet built.**

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

## Information layout

For now this is a **content + analysis workspace**, not yet a code tool. One
folder per adventure, each with the same simple split:

```
adventure-scripts/
└── <adventure-name>/
    ├── source/     # the original script(s) as received — never edited in place
    ├── analysis/   # skeletons, encounter ledgers, improvement notes
    └── drafts/     # revised / improved versions of the script
```

The rule: **`source/` is read-only history**, `analysis/` is where we reason
about a script, and `drafts/` holds the improved output. That keeps the
original recoverable while we iterate.

Current adventures:

| Adventure | Status |
|-----------|--------|
| [`paper-chase/`](paper-chase/) | Analyzing — skeleton + encounter/benefit ledger in [`analysis/`](paper-chase/analysis/) |

## When this grows into a code tool

It will follow the same monorepo conventions as the other tools:

- its own `requirements.txt`, installed into the repo-root `../../.venv`;
- paths resolved relative to the tool's own entry point;
- generated output under `build/` (git-ignored);
- reusable helpers promoted to the cross-game [`../../shared/`](../../shared/)
  only once a second tool needs them.
