#!/usr/bin/env python3
"""Update README image version query so GitHub refreshes cached SVG images."""

from __future__ import annotations

import os
import pathlib
import re
import time

README = pathlib.Path("README.md")
VERSION = os.getenv("STATS_VERSION") or time.strftime("%Y%m%d%H%M%S", time.gmtime())

STATS_URL = f"https://raw.githubusercontent.com/songs66/songs66/main/assets/github-stats.svg?v={VERSION}"
LANGS_URL = f"https://raw.githubusercontent.com/songs66/songs66/main/assets/top-langs.svg?v={VERSION}"

text = README.read_text(encoding="utf-8")

text = re.sub(
    r"(?:https://raw\.githubusercontent\.com/songs66/songs66/main/assets/github-stats\.svg\?v=[^"]+|\.\/assets\/github-stats\.svg)",
    STATS_URL,
    text,
)
text = re.sub(
    r"(?:https://raw\.githubusercontent\.com/songs66/songs66/main/assets/top-langs\.svg\?v=[^"]+|\.\/assets\/top-langs\.svg)",
    LANGS_URL,
    text,
)

README.write_text(text, encoding="utf-8")
