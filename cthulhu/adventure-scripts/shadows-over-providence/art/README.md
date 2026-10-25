# Shadows over Providence — art

`prompts.yaml` is the committed list of images the scenario needs: NPC portraits,
key objects, scene illustrations, and two in-world "handout" photographs (Mary
Mazars's flash prints of the death and of the haze).

Generated images go to `../build/art/` (git-ignored). Accepted images are recorded
in `../build/art/gallery.json`.

## Review and generate

The review app lives with the D&D tooling and is pointed at this folder with `--base`.
Run it on the dev VM from the repo root:

```bash
.venv/bin/python dnd/tools/art_review.py --base cthulhu/adventure-scripts/shadows-over-providence
```

It binds `0.0.0.0:5005`, so open `http://<vm-ip>:5005` in the host browser. Each card
has a model picker. The default is OpenAI's `gpt-image-2.5-sunburst` (best quality);
`gpt-image-2.5-flare` is faster and cheaper for drafts. Keys come from
`credentials/env.production`.

Edits made in the app live in `gallery.json`. Copy a prompt back into `prompts.yaml`
once you're happy with it, so it survives.
