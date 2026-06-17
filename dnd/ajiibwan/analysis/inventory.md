# Ajiibwan Corpus — Inventory

A catalogue of the source material in Google Drive
(`gdrive-personal:Personal/doc/RPG/Ajiibwan`), exported into `../assets/_raw/`.
This is the raw-material survey that the conversion/indexing pipeline (Phase 2)
and adventure design build on. See [`story-structure.md`](story-structure.md) for
the narrative read of this same material.

## At a glance

| Metric | Value |
|--------|-------|
| Total files | **1,755** |
| Total size | **~5.6 GB** |
| Directories | 117 |
| Google Docs (Steve's own writing) | **51** (→ exported to markdown) |
| Google Sheets | 5 (→ exported to `.xlsx`) |
| Images (png/jpg/jpeg/webp/svg) | **~1,444** |
| PDFs | 200 |
| Zips (map/asset packs) | 29 |
| Audio (mp3/webm) | 4 |
| Other (txt, epub, vtt, etc.) | ~12 |

**The knowledge-base value is concentrated in the 51 Google Docs** (~171k words of
Steve's own world lore, adventures, and play history). The other ~5.5 GB is
**reference/source assets** — maps, portraits, token art, and *commercial* adventure
PDFs / battlemap packs — much of it third-party copyrighted. See
[Recommended git policy](#recommended-git-policy).

## Tier 1 — Core knowledge base (homebrew writing)

These are the documents that define the world and its play. All exported to markdown.

### World & lore
| Doc | ~Words | What it is |
|-----|-------:|------------|
| `Lore - Ajiibwan Wilderlands .md` | 15,191 | **The master world bible** — geography, history, factions, cosmology, house rules, NPCs by location. |
| `Lore - Primary Source materials.md` | 4,783 | In-world primary sources (researcher notes, dream catchers, the imprisoned titan). |
| `Lore - Map fragments and Other Records.md` | 568 | Map fragments / scattered records. |
| `New Players Guide to the Ajiibwan Desert.md` | 1,020 | Player-facing onboarding (tone, how to arrive in Tel A'bib). |

### Campaign state & play history (the sequencing backbone)
| Doc | ~Words | What it is |
|-----|-------:|------------|
| `Journal - Ajiibwan Meetup game - Party Notes.md` | 64,202 | **Prior party's journal** — what the players did, session by session. |
| `GM Game Notes - Ajiibwan Meetup game.md` | 40,772 | **GM's running notes** — sequence, NPCs, loot, world reactions. |
| `Strongbox - Ajiibwan Meetup game.md` | 25,079 | Party loot/inventory/treasure ledger. |
| `Ajiibwan Games Notes 2026.md` | 204 | Most recent notes (the re-launch starting point). |

### Rules & house systems
| Doc | What it is |
|-----|------------|
| `How to Create a Character.md` | Character-creation house rules (no standard Wizard/Sorcerer/Warlock; start L2→L3; standard array). |
| `Travel, Gaming and Trading Rules (...).md` | Overland travel, trading economy, Dragonchess, drinking/racing minigames. |
| `Bokkaran Artificer Infusions.md` | Custom Bokkaran infusion list (~15k words). |
| `Adventure Template.md` | **The GM's adventure schema** — the field structure to mirror in `scenarios/*.yaml` (see story-structure). |

### Adventures, grouped by region/location
The world is organized as numbered adventure sites. Folder names encode metadata:
**`Name (index#) (level range) HEX-coord`**, e.g. *Kantaron — Tinkerer's Workshop (1)
(Level 3-6) 1810* = adventure #1, levels 3–6, hex 1810. The **"Shunned #1–4"** tag marks
a connected arc. Adventure docs found (folders with homebrew `.docx`):

- **Saragubi Desert & Pyramid of the Lost King** (19, L1-5, 0515) — 6 docs (Kalinore's tomb arc, navigating/escaping the desert).
- **Granite Empire** — 6 docs (Slumbering Titan; Al Faiz & Sefurah Springs sub-arc; The Tugari in Need).
- **Holy Cities (Bluffside)** (6, 0822) — 4 docs ("The Dark Arts" cult/diplomacy series).
- **Sea of Souls** — 3 docs (Mesos' Dock, trade-route & cavern adventures).
- **Kantaron — Tinkerer's Workshop** (1, L3-6, 1810) — 3 docs (summit crisis, Nalfeshnee pursuit).
- **Hothme** (x, 0117) — 3 docs (exploring the Granite Empire; Valeska's Needle).
- **B'rath** (13, 1412) — 3 docs (Freeing Mesos; Titan's Finger & Fire Beetles).
- **Slave Trade** — 2 docs (stopping the slavers and those behind them).
- Single-doc sites: **Air Spire** (2), **Bokkaral**, **Bridged City — Scholarly Schism** (Shunned #2, 11),
  **Chandler's Folly — Radiant Necropolis** (2510), **Crystal Towers** (29, 1414),
  **Dimark** (L3-4, 1210), **Djeteke — Jarab** (25, 1317).
- `Archive/Ajiibwan GM Player Notes - Golino.md`, `A-Player Characters/Untitled document.md` — misc.

### Sheets (tabular data → `.xlsx`)
`Random Open World Areas` (open-world generator tables + magic-consequences table),
`Critical Codex`, `Party Spellbook`, `D&D Level up calculations`,
`Summon Fey Spell - Fey List`.

## Tier 2 — Reference / source assets (bulk, mostly not homebrew text)

- **`A-Maps/`, `A-Wilderlands source maps/`** — the campaign world maps (incl. hex maps
  `Campaign_Map_07*`, region maps, annotated Tel A'bib). **High value** for the world.
- **`A-Portraits/`, `A-Silhouettes/`, `A-Player Characters/`** — NPC/PC portrait & token art.
- **`A-Unplaced Adventures/`** — purchased modules + large battlemap zips not yet sited
  in the world (e.g. *Whispers of War*, *Of Dryads and Men*, *The Fog Has Eyes*).
- **Per-site folders** also hold maps and, often, the **commercial PDF module** the site
  was adapted from (e.g. *Pyramid_of_the_Lost_King.pdf*, *Darkness Gathers...*).
- **`Z-Open World Generator source material/`, `Y-...` Scarred Lands / Shunned references** —
  third-party sourcebooks used as inspiration.
- **Audio**: `Doom in the Desert.mp3`, `Excalibur's Call.mp3` (ambience/theme).
- Many adventure folders contain **0 homebrew docs** — their content lives only as a
  commercial PDF + maps (e.g. *Eye of Kings*, *Oasis of Sia*, *Forsaken Pyramid*,
  *Beneath the Festered Sun*, *Port of Dakhalla*, the *City of* sites). These are sited
  in the world (hex + level) but not written up by Steve.

## Git policy (decided)

Everything currently lands in `assets/_raw/` (fully git-ignored, ~5.6 GB). Graduation
into committed `assets/` during Phase 2:

- **Commit (text):** the 51 converted `.md` + the 5 `.xlsx` (small, the actual IP, diffable).
- **Reference-in-place, do NOT commit:** all images/maps, portraits/token packs, the 29
  zips, the 200 (mostly commercial) PDFs, audio. `INDEX.md` catalogs them **by path** so
  they're findable, without putting binaries or copyrighted material in the repo.

> **Maps live in Roll20, not the repo.** Steve runs the game from Roll20, which holds the
> world map and world-tracking (a habit from the 5-year online campaign). So the tooling
> does **not** manage maps: it stays focused on lore/structure/scenario text. When a new
> map is needed, Steve uploads it to Roll20 (optionally with our help generating it).
