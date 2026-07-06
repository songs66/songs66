#!/usr/bin/env python3
"""Update README image version query so GitHub refreshes cached SVG images."""

from __future__ import annotations

import os
import pathlib
import re
import time

OWNER = "songs66"
REPO = "songs66"
README = pathlib.Path("README.md")
VERSION = os.getenv("STATS_VERSION") or time.strftime("%Y%m%d%H%M%S", time.gmtime())


def build_raw_url(svg_name: str) -> str:
    return f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/assets/{svg_name}.svg?v={VERSION}"


def refresh_svg_url(text: str, svg_name: str) -> str:
    """Replace either local or raw GitHub SVG URLs with a fresh cache-busting URL."""
    escaped_owner = re.escape(OWNER)
    escaped_repo = re.escape(REPO)
    escaped_svg = re.escape(svg_name)

    pattern = (
        rf"(?:https://raw\.githubusercontent\.com/{escaped_owner}/{escaped_repo}/main/assets/{escaped_svg}\.svg"
        rf"|\.\/assets\/{escaped_svg}\.svg)"
        rf"(?:\?v=[^\"'<>\s)]*)?"
    )

    updated_text, replacements = re.subn(pattern, build_raw_url(svg_name), text)

    if replacements == 0:
        raise RuntimeError(
            f"Could not find assets/{svg_name}.svg in README.md. "
            "Please check the README image src path."
        )

    return updated_text


def main() -> None:
    text = README.read_text(encoding="utf-8")
    text = refresh_svg_url(text, "github-stats")
    text = refresh_svg_url(text, "top-langs")
    README.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
