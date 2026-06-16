# rpg-gen

A growing collection of generators and tooling for tabletop RPGs — a small
**monorepo**. Work is grouped **one folder per game**; each game holds its own
self-contained tools, and game-agnostic code graduates into [`shared/`](shared/)
once more than one game needs it.

## Games

| Game | What's here | Status |
|------|-------------|--------|
| [`cthulhu/`](cthulhu/) | *Call of Cthulhu* 7e — character-sheet rendering and adventure-script tooling. | ✅ active |

More games (D&D, Pathfinder, …) get their own top-level folder as they appear.

## Layout

```
rpg-gen/
├── cthulhu/              # game: Call of Cthulhu 7e
│   ├── character-sheets/ #   tool: investigator dossiers → HTML/PDF
│   └── adventure-scripts/#   tool: adventure script generation/revision
├── shared/               # game-agnostic libraries, tools, and agent instructions
├── .venv/                # one shared Python virtualenv for the whole repo
├── LICENSE
└── README.md             # you are here
```

Two levels of grouping:

- **Per game** — each top-level game folder (`cthulhu/`) carries its own README
  index and the tools specific to that system.
- **Per tool** — each tool folder is self-contained: its own `README.md`,
  `requirements.txt`, templates, data, and `build/` output. Paths inside a tool
  resolve relative to that tool's own directory, so tools never reach across
  into each other.

## Conventions

- **Game folder at the top, tool folder inside it.** A tool lives at
  `<game>/<tool>/`; the game folder's README is its tool index.
- **One shared virtualenv** at the repo root (`.venv/`). Each tool declares its
  own dependencies in its `requirements.txt`; install them all into the root
  venv (from a tool folder, two levels up):
  ```bash
  python3 -m venv .venv --system-site-packages
  for req in */*/requirements.txt; do .venv/bin/pip install -r "$req"; done
  ```
- **`build/` and `dist/` are git-ignored** wherever they appear, so each tool
  writes generated artifacts under its own folder without polluting the repo.
- **Shared code is extracted, not anticipated.** A helper graduates into
  `shared/` when something *outside its game* needs it — see
  [`shared/README.md`](shared/README.md). Game-specific helpers stay under the
  game folder.

## Adding a game

1. Create a top-level folder named for the system (e.g. `dnd/`).
2. Give it a `README.md` index listing its tools.
3. Add a row to the **Games** table above.

## Adding a tool

1. Create a folder under the relevant game (e.g. `cthulhu/handouts/`).
2. Give it a `README.md` and a `requirements.txt`.
3. Resolve paths relative to the tool's own entry-point file (e.g.
   `ROOT = Path(__file__).resolve().parent`) so it stays self-contained.
4. Add a row to that game's tool table.

## License

[Apache License 2.0](LICENSE).
