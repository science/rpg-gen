# Character Sheets — working notes for Claude

A character factory for *Call of Cthulhu* 7e. Each investigator is one YAML file
in `characters/`; `build.py` renders it (via Jinja2 + WeasyPrint) to a 1920s Art
Deco dossier in `build/`. The renderer is **tolerant** — every section is
optional and missing data prints as blank ruled fill-in space. See
[`docs/metadata-schema.md`](docs/metadata-schema.md) for the authoritative field
list and [`characters/mercure.yaml`](characters/mercure.yaml) for the reference
example.

## Files & layout

- `characters/*.yaml` — one investigator each. **`build.py --all` globs
  `characters/*.yaml`**, so anything in this dir ending in `.yaml`/`.yml` renders
  as a real character.
- `characters/_template.yaml.example` — the blank, commented starting point. The
  `.yaml.example` extension is deliberate: it keeps the template OUT of `--all`.
  Do not rename it to `.yaml`.
- `templates/sheet.html.j2`, `templates/_macros.j2` — layout. `static/css/deco.css`
  — the single stylesheet (browser + print).
- `build/<name>.{html,pdf}` — output.

## Commands

Run from this `character-sheets/` directory; the venv lives at the repo root (two levels up).

```bash
../../.venv/bin/python build.py iris --html-only   # fast preview, no native deps
../../.venv/bin/python build.py iris                # html + pdf
../../.venv/bin/python build.py --all               # every characters/*.yaml
```

A harmless `RuntimeWarning: Unexpected value in sys.prefix` prints because the
venv is one dir up; ignore it.

## Methodology: creating a new investigator from a player brief

This is the process used to build `characters/iris.yaml` from a player's sketch.
Follow it when a player hands you a character idea.

1. **Start from the template, not from scratch.**
   `cp characters/_template.yaml.example characters/<name>.yaml`. The template is
   a generalized abstraction of the Mercure sheet — same section spine, neutral
   placeholders, inline guidance comments.

2. **Find the motivation engine first.** A sheet works when one contradiction
   drives everything. Mercure: a *trick-master who aches for a real miracle*.
   Iris: a *materialist who has seen a crack in the material world*. Put that
   tension in `backstory.ideology_beliefs` and let every other section serve it.
   Tie it to the seed of the character's pull toward the Mythos.

3. **Build the character to NOT replicate the player, and to NOT overlap the
   party.** Give them a niche the rest of the table lacks (Iris owns Drive /
   Mechanical Repair / **Intimidate** precisely because the others reach for
   charm and fast talk). Coordinate `pocket_litter` and `suggested_skills_flavor`
   so signature gear and skills don't collide with existing investigators —
   Mercure's file even notes "another investigator carries the flash powder."

4. **Ground a complex background concretely and historically.** Anchor it to a
   real place/era that makes the concept plausible (Iris's mixed heritage is set
   in the genuinely multi-ethnic New Bedford whaling world; her mentor's "the
   other side" is the Kabbalistic *sitra achra*). Put the long version in
   `birthplace.notes` and `career_arc` (both reference-only, not rendered) so the
   rendered prose stays consistent.

5. **Fill the six backstory sections as a connected web, ~4 entries each.**
   `significant_people` reliably wants: a **mentor** (often deceased — doubles as
   motivation + mystery hook), a **rival/adversary** (standing pressure), a
   **loyal confidant**, and **family** (a strained tie to where they came from).
   `meaningful_locations` wants a workplace, a social hub, a place for the secret
   occult interest, and a roots/home anchor. Cross-link people to locations and
   possessions so the world feels whole.

6. **Use `treasured_possessions` to plant Keeper hooks.** Always include one
   arcane volume/artifact with `(Keeper hook: ... TBD by the Keeper.)` so numeric
   stats, sanity, and spell content stay the Keeper's call.

7. **Keep this file backstory-only.** Numeric STR/CON/skill values come from an
   external PDF generator — never invent them. `keeper_notes` (not rendered)
   carries `hooks` and `suggested_skills_flavor` for the Keeper.

8. **Honor table conventions about sensitive material.** This table's standing
   rule: racism exists in 1921 but stays **off-stage**; ethnic identity is written
   as real texture and as a source of strength, never centered as a wound the
   table pokes at. Record any such convention in `keeper_notes` (see
   `iris.yaml`'s `keeper_notes.table_convention`) so it travels with the file.

9. **Render and eyeball before handing it over.**
   `build.py <name> --html-only`, open `build/<name>.html`. Check the masthead
   (omit `identity.stage_name` for non-performers — it falls back to
   `legal_name`), the ID grid, and that prose isn't truncated. Then build the PDF.

### Field cheatsheet for the masthead

- `stage_name` → big masthead title; **omit it** for non-performers to fall back
  to `legal_name`.
- `billing` → italic subtitle; repurpose as a one-line descriptor/tagline.
- `known_as` → appended after the legal name on the masthead; include your own
  quote marks, it's rendered verbatim.
