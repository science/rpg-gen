# shared

Code used by **more than one** tool in this monorepo.

Empty for now, by design. The rule is **extract on the second use, not the
first**: when a second tool needs something `character-sheets/` already does —
loading/validating YAML, building a Jinja environment, the Art Deco CSS, the
WeasyPrint HTML→PDF step — lift that piece here and have both tools import it.

Until then, keeping helpers next to their only caller is simpler than a shared
package no one else uses.

## When you do add something here

- Give it a clear module name (e.g. `cthulhu_render.py`, `yaml_doc.py`).
- Tools import it by adding this directory to the path, or by installing
  `shared/` as an editable package — decide when the first real shared module
  appears.
- Keep it dependency-light; a tool should be able to use one helper without
  dragging in another tool's stack.
