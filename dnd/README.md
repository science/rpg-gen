# D&D 5e

Tools and content for *Dungeons & Dragons* 5th edition — one game's worth of the
[rpg-gen](../README.md) monorepo. Everything D&D-specific lives under this folder;
game-agnostic helpers graduate up to [`../shared/`](../shared/).

Unlike `cthulhu/` (which groups one tool per folder), D&D is organized
**campaign-first**: a single set of reusable scripts in [`tools/`](tools/) operates
on per-campaign content folders. The first — and currently only — campaign is the
homebrew world **Deserts of Ajiibwan** in [`ajiibwan/`](ajiibwan/).

## Layout

```
dnd/
├── tools/            # reusable, campaign-agnostic scripts
│   ├── convert.py    #   raw gdrive export (md + PDFs) -> clean markdown assets
│   ├── index.py      #   scan a campaign's assets/ -> INDEX.md, GLOSSARY.md, entities.yaml
│   ├── render.py     #   scenario YAML -> HTML/PDF GM packet (Jinja2 -> WeasyPrint)
│   └── art.py        #   text prompt -> image via Replicate (pluggable provider)
└── ajiibwan/         # campaign: Deserts of Ajiibwan (5-year homebrew world)
    ├── assets/       #   world lore converted from Google Docs/PDFs (committed)
    ├── analysis/     #   inventory + story-structure reads of the corpus
    ├── campaign/     #   live state: party, threads, session logs, entities
    ├── scenarios/    #   "what's next" adventure packets
    ├── templates/    #   Jinja2 templates for rendered packets/handouts
    └── build/        #   rendered PDFs + generated art (git-ignored)
```

## Two capabilities

1. **Knowledge base** (`tools/convert.py` + `tools/index.py` → `ajiibwan/assets/`) —
   five years of campaign material lives in Google Docs and PDFs. We convert it to
   committed markdown and generate an index/glossary/entity list so adventure design
   can connect what the players do to the wider world's lore. *(Semantic search via
   embeddings is a deferred follow-up.)*
2. **Adventure manager + event designer** (`ajiibwan/campaign/` + `ajiibwan/scenarios/`
   + `tools/render.py` + `tools/art.py`) — track current campaign state and design the
   next scenarios (themes, locations, NPCs, monsters, goals, rewards, GM guides, art).

See [`CLAUDE.md`](CLAUDE.md) for the working methodology (conversion, indexing, and
"what's next" scenario design).

## Conventions

Follows the repo-wide rules (see [`../README.md`](../README.md)):

- **Reusable code in `tools/`, content under the campaign folder.** A second campaign
  in this world gets its own sibling of `ajiibwan/` and reuses the same `tools/`.
- **The shared virtualenv** lives at the repo root (`../../.venv` from inside `dnd/`),
  so commands run as `../../.venv/bin/python tools/<script>.py …`.
- **Dependencies** are declared once in [`requirements.txt`](requirements.txt) and
  installed into the root venv.
- `ajiibwan/build/` and `ajiibwan/assets/_raw/` are git-ignored; the *converted*
  markdown under `assets/` IS committed.

## Host vs VM note

rclone/Google Drive runs on the **host OS**, not this dev VM. Steps that read Drive
(the `rclone` exports feeding `assets/_raw/`) must run on the host; everything else
(conversion, indexing, rendering, art) runs anywhere. The repo is bind-mounted, so
host-written files appear here immediately. See [`CLAUDE.md`](CLAUDE.md).
