# Character metadata schema

Each character is a single YAML file under `characters/`. The renderer is
**tolerant**: every section is optional, and any section that is missing (or
present but empty) is rendered as blank, ruled fill-in space. That is by
design — a sheet is meant to be printed half-empty and filled in over play.

This document describes the fields the templates currently read. Add fields
freely; unknown keys are simply ignored by the renderer.

## Top-level keys

| Key | Type | Notes |
|-----|------|-------|
| `meta` | map | `setting`, `ruleset`, etc. Only `setting` is shown (in the ID grid). |
| `identity` | map | Core nameplate / ID-grid data. |
| `birthplace` | map | `location` is shown in the ID grid; `notes` is reference only. |
| `backstory` | map | The six classic 7e backstory sections. |
| `wealth` | map | Spending level, cash, assets. |
| `inventory` | map | `gear` list (pocket litter has its own top-level key). |
| `pocket_litter` | list | `{item, desc}` — carried-on-person items. |
| `weapons` | list | `{name, skill, damage, range, attacks, ammo, malfunction}`. |
| `injuries_scars` | list | `{name, desc}` — accrues over play. |
| `phobias_manias` | list | `{name, desc}` — accrues over play. |
| `arcane` | list | `{name, type, notes}` — tomes, spells, artifacts. |
| `encounters` | list | `{name, desc}` — encounters with strange entities. |
| `keeper_notes` | map | **Not rendered** on the player sheet. Keeper-eyes-only. |

## `identity`

```yaml
identity:
  legal_name: "Esther Mae Calloway"   # nameplate sub-line
  known_as: "“Essie”"                  # optional nickname (include your own quotes; rendered verbatim after the legal name)
  stage_name: "Mademoiselle Mercure"   # big masthead title (falls back to legal_name)
  billing: "The Quicksilver Conjuress" # italic sub-title under the masthead
  sex: "Female"
  age: 32
  occupation: "Stage Magician"
  residence: "Providence, Rhode Island"
  status: "Regional headliner"         # shown as "Standing"
```

## `backstory`

```yaml
backstory:
  personal_description: "prose..."     # string
  ideology_beliefs: "prose..."         # string
  significant_people:                  # list of {name, relation, desc}
    - {name: "...", relation: "Mentor", desc: "..."}
  meaningful_locations:                # list of {name, desc}
    - {name: "...", desc: "..."}
  treasured_possessions:               # list of {name, desc}
    - {name: "...", desc: "..."}
  character_traits:                    # list of strings (bulleted)
    - "Quick-fingered and observant"
```

## New sections (added for the secondary sheets)

These are the fields the design introduces beyond the original Mercure file.
They are all optional — leave them out to print blank fill-in space.

```yaml
wealth:
  spending_level: "Average ($10/day)"
  cash: "$84 on hand"
  assets: "$2,000"
  credit_rating: "55"
  asset_details:
    - "1916 touring car, much-repaired"
    - "Trunk of stage apparatus (insured $400)"

inventory:
  gear:                                # everyday kit beyond pocket litter
    - {item: "Steamer trunk", desc: "Hidden-compartment performing trunk."}

weapons:
  - name: "Derringer .41"
    skill: "20"
    damage: "1D10"
    range: "3 yds"
    attacks: "1"
    ammo: "2"
    malfunction: "100"

injuries_scars:
  - {name: "Burned left forearm", desc: "A fire-cabinet trick gone wrong, 1919."}

phobias_manias:
  - {name: "Claustrophobia", desc: "After the box jammed in Hartford."}

arcane:
  - {name: "De Vermis Mysteriis", type: "Tome", notes: "Latin; +Cthulhu Mythos."}

encounters:
  - {name: "The thing in the cabinet", desc: "Providence, 1921. Sanity loss 1/1D6."}
```
