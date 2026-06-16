# shared

Game-agnostic code, tools, and agent instructions used by **more than one
game** in this monorepo.

Empty of modules for now, by design. The rule is **extract on the second use,
not the first**: a helper graduates here only when something *outside its
original game* needs it. Until a second game (D&D, Pathfinder, …) actually
appears, Cthulhu-only helpers stay under [`../cthulhu/`](../cthulhu/) next to
their only caller — a shared package no one else imports is just indirection.

## Abstraction candidates (analyzed, not yet extracted)

These were identified as genuinely game-agnostic while restructuring the repo.
They are documented here so the extraction is a lift-and-rename when the second
consumer arrives — not a rediscovery.

### Document render pipeline → `render/` (Python)

`cthulhu/character-sheets/build.py` is a thin YAML → Jinja2 → HTML → WeasyPrint
pipeline. The mechanics are game-agnostic; only the templates, CSS, and schema
are Cthulhu-specific. The reusable core:

| Function (today, in `build.py`) | What it does | Game-specific? |
|---------------------------------|--------------|----------------|
| `load_character(path)` | load a YAML file, assert it's a top-level mapping | no — pure YAML |
| `make_env()` | build a Jinja `Environment` over a templates dir | no — pass the dir in |
| `render_html(data, env)` | render a named template with a data dict + CSS string | mostly — generalize the template name + CSS source |
| `resolve_target(arg)` | resolve a bare name against a data dir (`.yaml`/`.yml`) | no — pass the dir + extensions in |
| `build_one(...)` + the `--all`/`--out`/`--html-only` CLI | glob a data dir, render each to `build/`, lazy WeasyPrint import | no — a generic "render every data file in a dir" driver |

A future `shared/render/doc_render.py` would expose roughly
`load_yaml_mapping(path)`, `make_jinja_env(templates_dir)`,
`render_pdf(html, base_url, out_path)`, and a `build_all(data_dir, templates_dir,
out_dir, ...)` driver. A character sheet then becomes *templates + CSS + schema*
and a few lines of glue; a D&D statblock or a handout tool reuses the same core.

### Agent instructions → `agent-instructions/` (Markdown)

The per-tool `CLAUDE.md` files capture **methodology** (e.g. how to build an
investigator from a player brief, table-convention handling) alongside
game-specific field references. The methodology spine — "find the motivation
engine first," "don't replicate the player or overlap the party," "plant Keeper
hooks" — generalizes to character creation in any system. When a second game
needs the same playbook, split the system-neutral guidance into a shared
instruction file that game-specific `CLAUDE.md`s reference.

## When you do extract something here

- Give it a clear module/file name (`doc_render.py`, not `utils.py`).
- Keep it **dependency-light**: a tool should be able to use one helper without
  dragging in another tool's stack (e.g. WeasyPrint stays a lazy import).
- Tools import shared code by adding this directory to the path, or by
  installing `shared/` as an editable package — decide when the first real
  module lands.
