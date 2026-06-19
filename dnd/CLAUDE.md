# D&D 5e — working notes for Claude

Campaign tooling for *Dungeons & Dragons* 5e. Reusable scripts live in `tools/`;
each campaign is a content folder (currently only `ajiibwan/`). Two jobs: build a
**knowledge base** from years of Google Docs/PDFs, and run an **adventure manager**
that designs "what's next" on top of that lore.

## Commands

Run from this `dnd/` directory; the venv lives at the repo root (two levels up).

```bash
# one-time install
../../.venv/bin/pip install -r requirements.txt

# convert raw gdrive exports -> clean markdown assets (after a host-side rclone export)
../../.venv/bin/python tools/convert.py ajiibwan

# (re)build the index/glossary/entities from the converted assets
../../.venv/bin/python tools/index.py ajiibwan

# render a scenario packet to HTML/PDF
../../.venv/bin/python tools/render.py ajiibwan/scenarios/<name>.yaml --html-only

# generate one image (needs REPLICATE_API_TOKEN; --fake for an offline placeholder)
../../.venv/bin/python tools/art.py --prompt "..." --out ajiibwan/build/art/x.png

# review/regenerate/accept scenario art in a local web app (binds 0.0.0.0:5005)
../../.venv/bin/python tools/art_review.py ajiibwan
```

## Host vs VM — Google Drive access

rclone is configured on the **host OS only** (`gdrive-personal` → `~/gdrive/personal`),
NOT on this dev VM. The repo (`~/dev/rpg-gen`) is bind-mounted between host and VM, so
files written on the host appear here instantly; `~/gdrive` is **not** shared.

Therefore the Drive-reading steps run on the host and write into the repo:

```bash
# [HOST] discover the campaign root, then export Docs->md and copy PDFs as-is:
rclone copy "gdrive-personal:<CampaignRoot>" \
    ~/dev/rpg-gen/dnd/ajiibwan/assets/_raw/ \
    --drive-export-formats md         # Google Docs come down as .md (real files, not URL stubs)
```

`assets/_raw/` is git-ignored staging. Everything downstream (`convert.py`, `index.py`,
rendering, art) runs on the VM. When a step needs the host, ask Steve to switch you there.

## Knowledge base: conversion + indexing

- **`tools/convert.py <campaign>`** reads `<campaign>/assets/_raw/`, converts each source
  into a clean `<campaign>/assets/<slug>.md` with YAML frontmatter
  (`title`, `source_path`, `type`, `converted`, `tags`):
  - gdoc-exported `.md` → normalized (fix heading levels, strip export cruft).
  - PDFs → `pymupdf4llm` text extraction. **Scanned/image-only PDFs** won't extract text;
    flag them in the run summary rather than emitting empty files — OCR (tesseract) is a
    deferred follow-up, not a silent drop.
- **`tools/index.py <campaign>`** scans `<campaign>/assets/*.md` and (re)generates:
  - `assets/INDEX.md` — table of contents grouped by source folder/topic.
  - `assets/GLOSSARY.md` — recurring proper nouns / terms with first-mention links.
- Commit the converted `assets/*.md` and the generated index files; keep `_raw/` ignored.

## World compendium (`<campaign>/world/`)

The deep, organized catalog of the world — synthesized by reading the full corpus and
merging/deduping into per-category references: `gazetteer.md` (places), `adventures.md`,
`cast.md` (people), `factions.md`, `artifacts.md`, `bestiary.md`, `lore-and-mysteries.md`,
and the machine-readable **`entities.yaml`** (the cross-link source of truth — ~300+
entities with `id`, `type`, `region`, `status`, `summary`, `sources`, `related`). This is
what adventure design reads first to reuse established world. It's an AI-synthesized draft
over the corpus: it preserves source conflicts rather than resolving them, and improves
with GM edits. See `world/README.md` for caveats.

## Maps & world-tracking live in Roll20

The game is run from **Roll20**, which holds the world map and world-tracking. This tooling
does **not** manage maps — it focuses on lore, structure, and scenario text. Source images
in `assets/_raw/` are reference-only (git-ignored, cataloged by path in `INDEX.md`), never
committed. When a scenario needs a new map, it's generated/handed off for upload to Roll20.

## Cross-linking convention

Campaign entities and scenarios reference lore by slug so design can pull relevant
background: `[[loc:hothme]]`, `[[npc:maghiel]]`, `[[faction:black-water-cult]]`,
`[[item:clasp-of-vergen]]`. A slug resolves to an `id:` record in
`world/entities.yaml` (and its full entry in the matching `world/*.md` compendium file).

## Campaign design principles (Ajiibwan game 2)

These shape the adventure manager — honor them when designing:

1. **Reset sandbox.** Game 2 rewinds the world to the **game-1 starting state**. The prior
   campaign (the `world/` compendium's `play_history`/`status`) is **reference only** —
   hooks, precedent, reusable scenarios — not inherited history. The new world starts
   pre-trigger (cult at full strength, demon unsummoned, Afra/Mesos dormant, sites unlooted,
   prior PCs absent). Seed `campaign/state.yaml` from the *start* state, not the compendium's
   end state.
2. **"RPG ouija board" — an indifferent living world.** The world goes where the party
   steers, but it **doesn't care about the party** and advances on its own whether or not
   they engage. Model factions/sites with their **own agendas and a world clock that ticks
   between sessions** regardless of party action — not a party-centric rail.
3. **In-world time runs faster than real time.** (Game 1 ran ≈1:1, ~2 weeks/session.) The
   campaign clock carries a configurable **dilation factor**; autonomous faction progression
   and the leveling cadence should read from it. Decouple "real sessions" from "in-world
   time elapsed."

## Adventure manager: campaign state

`ajiibwan/campaign/` is the live state of the *current* (new-players) run, seeded at the
game-1 start state (see principle 1):

- `state.yaml` — party roster, current location, **in-world date + clock dilation factor**,
  party level, milestones.
- `threads.yaml` — plot threads with status (`dormant` / `active` / `advancing` / `resolved`)
  **and an autonomous-progression note** (what the faction/thread does on its own each world
  tick if the party ignores it — principle 2).
- `sessions/NN.md` — one recap per session (what the players actually did).
- `entities/{npcs,locations,factions,monsters}/*.yaml` — structured records, consistent
  with the `cthulhu/character-sheets` YAML style; prose lives in markdown.

## Methodology: designing "what's next"

When asked to build the next scenario:

1. **Read the current state first.** `state.yaml` + the latest `sessions/*.md` + open
   `threads.yaml`. Design forward from where the party actually is, not a blank slate.
2. **Mine the knowledge base for connective tissue.** Use `assets/INDEX.md`,
   `GLOSSARY.md`, and `entities.yaml` to find established lore (places, NPCs, factions,
   history) the next scenario can reincorporate. Prefer paying off existing threads and
   foreshadowed elements over inventing disconnected new content.
3. **Anchor on one dramatic question.** A scenario works when a single tension drives it
   (mirror the character-sheets rule: one contradiction powers the whole sheet). State it
   at the top of the scenario YAML.
4. **Assemble the packet.** A scenario is `ajiibwan/scenarios/<name>.yaml` with: theme,
   hook (tied to a thread/lore slug), locations, NPCs, monsters/creatures, goals/objectives,
   rewards, and a GM guide (scene flow, pacing, contingencies). Reference lore by slug.
5. **Render and eyeball.** `tools/render.py` → HTML first, then PDF, into `ajiibwan/build/`.
6. **Art is optional and last.** `tools/art.py` turns key locations/NPCs into reference
   images via Replicate. Derive prompts from the scenario/entity YAML; never block packet
   creation on art.
7. **Close the loop after play.** Add a `sessions/NN.md` recap and update `state.yaml` /
   `threads.yaml` so the next design starts from accurate state.
