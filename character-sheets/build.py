#!/usr/bin/env python3
"""Cthulhu-Gen — render Call of Cthulhu 7e secondary character sheets from YAML.

The numeric stats page (STR/CON/skills...) is produced by an external PDF
generator. This tool renders the *secondary* sheets: backstory, inventory,
wealth, weapons, and the traits that accrue over play — in a 1920s Art Deco
style that flows across as many pages as the content needs.

Usage:
    python build.py characters/mercure.yaml      # -> build/mercure.{html,pdf}
    python build.py --all                         # render every characters/*.yaml
    python build.py mercure.yaml --html-only      # skip PDF
    python build.py mercure.yaml --out dist
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
CHARS = ROOT / "characters"
BUILD = ROOT / "build"


def load_character(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping at the top level")
    return data


def make_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "j2", "html.j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_html(data: dict, env: Environment | None = None) -> str:
    env = env or make_env()
    css = (STATIC / "css" / "deco.css").read_text(encoding="utf-8")
    return env.get_template("sheet.html.j2").render(c=data, css=css)


def resolve_target(arg: str) -> Path:
    """Accept a path, or a bare name resolved against characters/."""
    p = Path(arg)
    if p.exists():
        return p
    for cand in (CHARS / arg, CHARS / f"{arg}.yaml", CHARS / f"{arg}.yml"):
        if cand.exists():
            return cand
    raise FileNotFoundError(f"character not found: {arg}")


def build_one(path: Path, out_dir: Path, html_only: bool, env: Environment) -> None:
    data = load_character(path)
    html = render_html(data, env)
    out_dir.mkdir(parents=True, exist_ok=True)

    html_path = out_dir / f"{path.stem}.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"  html -> {html_path.relative_to(ROOT)}")

    if not html_only:
        from weasyprint import HTML  # imported lazily so --html-only needs no native deps

        pdf_path = out_dir / f"{path.stem}.pdf"
        HTML(string=html, base_url=ROOT.as_uri() + "/").write_pdf(str(pdf_path))
        print(f"  pdf  -> {pdf_path.relative_to(ROOT)}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("character", nargs="?", help="character YAML (path or name under characters/)")
    ap.add_argument("--all", action="store_true", help="render every characters/*.yaml")
    ap.add_argument("--html-only", action="store_true", help="skip PDF generation")
    ap.add_argument("--out", default=str(BUILD), help="output directory (default: build/)")
    args = ap.parse_args(argv)

    if not args.all and not args.character:
        ap.error("provide a character, or use --all")

    targets: list[Path]
    if args.all:
        targets = sorted(set(CHARS.glob("*.yaml")) | set(CHARS.glob("*.yml")))
        if not targets:
            ap.error(f"no characters found in {CHARS}")
    else:
        targets = [resolve_target(args.character)]

    env = make_env()
    out_dir = Path(args.out)
    for path in targets:
        print(f"{path.name}:")
        build_one(path, out_dir, args.html_only, env)
    return 0


if __name__ == "__main__":
    sys.exit(main())
