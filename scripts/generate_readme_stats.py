#!/usr/bin/env python3
"""Generate stable SVG cards for a GitHub profile README.

The README should reference the generated files in ./assets instead of calling
third-party dynamic image services at page-render time.
"""

from __future__ import annotations

import json
import os
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request
from html import escape
from typing import Any

USERNAME = os.getenv("GITHUB_USERNAME") or os.getenv("GITHUB_REPOSITORY_OWNER") or "songs66"
TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
OUTPUT_DIR = pathlib.Path(os.getenv("OUTPUT_DIR", "assets"))
API_ROOT = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "profile-readme-stats-generator",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

THEME = {
    "bg": "#0d1117",
    "border": "#30363d",
    "title": "#58a6ff",
    "text": "#c9d1d9",
    "muted": "#8b949e",
    "bar_bg": "#21262d",
}

LANG_COLORS = [
    "#58a6ff",
    "#f78166",
    "#a5d6ff",
    "#d2a8ff",
    "#7ee787",
    "#ffdf5d",
    "#ffa657",
    "#79c0ff",
]


def request_json(url: str) -> Any:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def paginated(url: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    separator = "&" if "?" in url else "?"
    page = 1
    while True:
        page_url = f"{url}{separator}per_page=100&page={page}"
        batch = request_json(page_url)
        if not isinstance(batch, list):
            break
        items.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return items


def format_number(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}k"
    return str(value)


def card_shell(width: int, height: int, body: str) -> str:
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img">
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{THEME['bg']}" stroke="{THEME['border']}"/>
  {body}
</svg>
'''


def stats_card(username: str, repos: list[dict[str, Any]], languages: dict[str, int]) -> str:
    non_forks = [repo for repo in repos if not repo.get("fork")]
    stars = sum(int(repo.get("stargazers_count") or 0) for repo in non_forks)
    forks = sum(int(repo.get("forks_count") or 0) for repo in non_forks)
    watchers = sum(int(repo.get("watchers_count") or 0) for repo in non_forks)
    main_language = max(languages, key=languages.get) if languages else "N/A"
    updated_at = time.strftime("%Y-%m-%d", time.gmtime())

    rows = [
        ("Public Repos", format_number(len(non_forks))),
        ("Total Stars", format_number(stars)),
        ("Total Forks", format_number(forks)),
        ("Watchers", format_number(watchers)),
        ("Main Language", main_language),
    ]

    text_rows = []
    y = 62
    for label, value in rows:
        text_rows.append(
            f'<text x="32" y="{y}" fill="{THEME["muted"]}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14">{escape(label)}</text>'
        )
        text_rows.append(
            f'<text x="210" y="{y}" fill="{THEME["text"]}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" font-weight="600">{escape(value)}</text>'
        )
        y += 24

    body = f'''
  <text x="32" y="34" fill="{THEME['title']}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" font-weight="700">{escape(username)}'s GitHub Stats</text>
  {''.join(text_rows)}
  <text x="32" y="176" fill="{THEME['muted']}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="11">Updated by GitHub Actions · {updated_at}</text>
'''
    return card_shell(430, 190, body)


def top_languages_card(languages: dict[str, int]) -> str:
    total = sum(languages.values())
    top = sorted(languages.items(), key=lambda item: item[1], reverse=True)[:6]

    if not top or total <= 0:
        body = f'''
  <text x="32" y="34" fill="{THEME['title']}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" font-weight="700">Top Languages</text>
  <text x="32" y="90" fill="{THEME['muted']}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14">No language data available yet.</text>
'''
        return card_shell(430, 190, body)

    rows = []
    y = 62
    bar_x = 154
    bar_width = 220
    for index, (language, bytes_count) in enumerate(top):
        percent = bytes_count / total * 100
        fill_width = max(2, int(bar_width * percent / 100))
        color = LANG_COLORS[index % len(LANG_COLORS)]
        rows.append(
            f'<text x="32" y="{y}" fill="{THEME["text"]}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" font-weight="600">{escape(language)}</text>'
        )
        rows.append(f'<rect x="{bar_x}" y="{y - 11}" width="{bar_width}" height="8" rx="4" fill="{THEME["bar_bg"]}"/>')
        rows.append(f'<rect x="{bar_x}" y="{y - 11}" width="{fill_width}" height="8" rx="4" fill="{color}"/>')
        rows.append(
            f'<text x="388" y="{y}" fill="{THEME["muted"]}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" text-anchor="end">{percent:.1f}%</text>'
        )
        y += 22

    body = f'''
  <text x="32" y="34" fill="{THEME['title']}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" font-weight="700">Top Languages</text>
  {''.join(rows)}
'''
    return card_shell(430, 190, body)


def collect_data(username: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    encoded = urllib.parse.quote(username)
    repos = paginated(f"{API_ROOT}/users/{encoded}/repos?type=owner&sort=updated")
    repos = [repo for repo in repos if not repo.get("archived")]

    languages: dict[str, int] = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        full_name = repo.get("full_name")
        if not full_name:
            continue
        url = f"{API_ROOT}/repos/{urllib.parse.quote(full_name, safe='/')}/languages"
        try:
            repo_languages = request_json(url)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            continue
        if not isinstance(repo_languages, dict):
            continue
        for language, byte_count in repo_languages.items():
            languages[language] = languages.get(language, 0) + int(byte_count)
    return repos, languages


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    repos, languages = collect_data(USERNAME)
    (OUTPUT_DIR / "github-stats.svg").write_text(stats_card(USERNAME, repos, languages), encoding="utf-8")
    (OUTPUT_DIR / "top-langs.svg").write_text(top_languages_card(languages), encoding="utf-8")


if __name__ == "__main__":
    main()
