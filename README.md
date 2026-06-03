# Cthulhu-Gen

A growing collection of generators and tooling for *Call of Cthulhu* 7th
edition — a small **monorepo**. Each tool stands on its own in a top-level
folder; over time they may lean on shared code in [`shared/`](shared/).

## Tools

| Tool | What it does | Status |
|------|--------------|--------|
| [`character-sheets/`](character-sheets/) | Renders 1920s Art Deco **secondary character sheets** (backstory, wealth, inventory, weapons, play-accrued traits) from a YAML file to HTML/PDF. | ✅ working |
| [`adventure-scripts/`](adventure-scripts/) | Create and improve **adventure scripts / scenarios** — drafting, structuring, and revising them. | 🚧 planned |

Shared, reusable code (YAML loading, Jinja helpers, common styling) lives in
[`shared/`](shared/) once more than one tool needs it — extract on the second
use, not the first.

## Layout

```
cthulhu-gen/
├── character-sheets/     # tool: investigator dossiers → HTML/PDF
├── adventure-scripts/    # tool: adventure script generation/revision (planned)
├── shared/               # libraries used by more than one tool
├── .venv/                # one shared Python virtualenv for the whole repo
├── LICENSE
└── README.md             # you are here
```

Each tool folder is self-contained: its own `README.md`, `requirements.txt`,
templates, data, and `build/` output. Paths inside a tool resolve relative to
that tool's own directory, so tools never reach across into each other.

## Conventions

- **One folder per tool**, named for what it produces (`character-sheets`,
  `adventure-scripts`). No nesting under `tools/` — the repo root *is* the
  tool index.
- **One shared virtualenv** at the repo root (`.venv/`). Each tool declares its
  own dependencies in its `requirements.txt`; install them all into the root
  venv:
  ```bash
  python3 -m venv .venv --system-site-packages
  for req in */requirements.txt; do .venv/bin/pip install -r "$req"; done
  ```
- **`build/` and `dist/` are git-ignored** wherever they appear, so each tool
  writes generated artifacts under its own folder without polluting the repo.
- **Shared code is extracted, not anticipated.** A helper graduates into
  `shared/` when a second tool needs it — see [`shared/README.md`](shared/README.md).

## Adding a tool

1. Create a top-level folder named for the output (e.g. `handouts/`).
2. Give it a `README.md` and a `requirements.txt`.
3. Resolve paths relative to the tool's own entry-point file (e.g.
   `ROOT = Path(__file__).resolve().parent`) so it stays self-contained.
4. Add a row to the **Tools** table above.

## License

[Apache License 2.0](LICENSE).
