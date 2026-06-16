# Character Sheets

> A *Call of Cthulhu* tool in the [rpg-gen](../../README.md) monorepo (see the
> [Cthulhu game index](../README.md)). Run the commands below from this
> `character-sheets/` directory; the shared virtualenv lives at the repo root.

A small **character factory** for *Call of Cthulhu* 7th edition.

The numeric stats page (characteristics, skills, combat values) is produced by
an external character PDF generator. This tool renders the **secondary
sheets** that those generators skimp on — backstory, wealth, inventory,
weapons, and the traits that accrue over play — in a **1920s Art Deco** style
designed to *flow across as many pages as the content needs* rather than being
crammed onto one.

Each character is a single YAML file in [`characters/`](characters/). Drop a
new file in and you get a new dossier — it is a factory, not a one-off.

## What it renders

A continuous, paginated dossier with:

- **Cover / nameplate** — stage name, billing, and an ID grid (player,
  occupation, birthplace, residence, standing…).
- **Backstory** — Personal Description · Ideology & Beliefs · Significant
  People · Meaningful Locations · Treasured Possessions · Character Traits.
- **Wealth & Means** — spending level, cash, assets, asset details.
- **Inventory** — pocket litter + gear.
- **Weapons** — standard 7e combat table.
- **Traits that accrue over play** — Injuries & Scars · Phobias & Manias ·
  Arcane Tomes, Spells & Artifacts · Encounters with Strange Entities.
- **Player Notes** — ruled space.

Every section that has no data yet is printed as blank, ruled fill-in space, so
a sheet is useful from session zero and grows with the character.

## Quick start

```bash
# one-time: create the shared venv at the repo root (see ../../README.md)
python3 -m venv ../../.venv --system-site-packages
../../.venv/bin/pip install -r requirements.txt

# render one character to build/
../../.venv/bin/python build.py characters/mercure.yaml

# render everything
../../.venv/bin/python build.py --all

# HTML only (no native PDF deps needed)
../../.venv/bin/python build.py mercure --html-only
```

Output lands in `build/<name>.html` and `build/<name>.pdf`.

## How it works

| Layer | Technology | Why |
|-------|-----------|-----|
| Data | **YAML** (`characters/*.yaml`) | human-editable, diff-friendly |
| Templating | **Jinja2** (`templates/`) | data-driven sections, reusable macros |
| Style | **CSS paged media** (`static/css/deco.css`) | one stylesheet, browser **and** print |
| Output | **WeasyPrint** | HTML/CSS → multi-page PDF |

Because the templates are plain HTML/CSS, you can preview a sheet by opening the
generated `.html` in any browser; WeasyPrint then produces the print-fidelity
PDF from the exact same markup.

See [`docs/metadata-schema.md`](docs/metadata-schema.md) for the full field
reference.

## Fonts

The sheets use Limelight, Cinzel, EB Garamond, and Special Elite, loaded from
Google Fonts at render time. (A future revision may vendor the fonts locally so
PDFs build fully offline.)

## License

[Apache License 2.0](LICENSE).
