# Call of Cthulhu

Tools and content for *Call of Cthulhu* 7th edition — one game's worth of the
[rpg-gen](../README.md) monorepo. Everything Cthulhu-specific lives under this
folder; game-agnostic helpers graduate up to [`../shared/`](../shared/).

## Tools

| Tool | What it does | Status |
|------|--------------|--------|
| [`character-sheets/`](character-sheets/) | Renders 1920s Art Deco **secondary character sheets** (backstory, wealth, inventory, weapons, play-accrued traits) from a YAML file to HTML/PDF. | ✅ working |
| [`adventure-scripts/`](adventure-scripts/) | Create and improve **adventure scripts / scenarios** — drafting, structuring, and revising them. | 🚧 workspace |

## Conventions

These follow the repo-wide rules (see [`../README.md`](../README.md)):

- **One folder per tool**, named for what it produces.
- Each tool is self-contained — its own `README.md`, `requirements.txt`,
  templates, data, and `build/` output — and resolves paths relative to its own
  entry point.
- The **shared virtualenv** lives at the repo root (`../../.venv` from inside a
  tool), so commands run from a tool folder use `../../.venv/bin/python`.
- A helper graduates into [`../../shared/`](../shared/) only when something
  outside Call of Cthulhu needs it; Cthulhu-only helpers stay here.
