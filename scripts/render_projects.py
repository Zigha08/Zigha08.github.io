#!/usr/bin/env python3
"""
render_projects.py — Render GitHub repo metadata to portfolio project cards.

Dipanggil oleh .github/workflows/sync-repos.yml.

Input:
  - $GITHUB_REPOS_JSON : JSON array repo (sudah di-fetch oleh workflow step sebelumnya).
                        Schema per item: {name, description, html_url, language,
                        stargazers_count, forks_count, pushed_at, topics, archived}
  - $INDEX_HTML_PATH   : Path ke index.html yang mau di-patch.

Output:
  - Stdout: string HTML baru untuk blok <div class="projects-grid">...</div>.
            Workflow yang akan replace placeholder di index.html dengan output ini.

Design choices:
  - Pakai string template biasa (bukan BeautifulSoup) untuk avoid dependency berat.
    Repo portfolio cuma butuh stdlib.
  - Sanitasi semua input via html.escape() untuk menghindari XSS injection
    dari description repo (yang isinya user-controlled di GitHub).
  - Sort by pushed_at desc, exclude archived & portfolio repo sendiri.
  - Limit 6 cards (portfolio grid max), biar tidak overflow design.
  - Date format: "Mon YYYY" (e.g. "Jun 2026").
"""

from __future__ import annotations
import html
import json
import os
import re
import sys
from datetime import datetime, timezone


# Pin list — repositori yang secara eksplisit di-include walaupun archived
# ataukah bukan. Kosongkan kalau mau full auto.
PINNED_REPOS: set[str] = set()

# Repositori yang di-exclude (mis. portfolio itu sendiri, atau repo test/private).
EXCLUDED_REPOS: set[str] = {"Zigha08.github.io", "Zigha08"}

# Maksimum jumlah card yang di-render.
MAX_CARDS = 6


def parse_pushed_at(s: str) -> datetime:
    """Parse ISO 8601 timestamp dari GitHub API."""
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def fmt_date(dt: datetime) -> str:
    """Format tanggal jadi 'Mon YYYY' (mis. 'Jun 2026')."""
    return dt.strftime("%b %Y")


def language_icon(lang: str | None) -> str:
    """Pakai label kosong jika bahasa None."""
    return html.escape(lang) if lang else "—"


def render_card(repo: dict) -> str:
    """Render satu project card. Return HTML string."""
    name = html.escape(repo["name"])
    desc = html.escape(repo.get("description") or "No description provided.")
    url = html.escape(repo["html_url"])
    lang = language_icon(repo.get("language"))
    stars = int(repo.get("stargazers_count") or 0)
    forks = int(repo.get("forks_count") or 0)
    dt = parse_pushed_at(repo["pushed_at"])
    date_label = fmt_date(dt)

    # Topics sebagai tag kecil (maks 3 biar tidak overflow).
    topics = repo.get("topics") or []
    topic_tags = ""
    if topics:
        topic_tags = " ".join(
            f'<span class="project-topic">{html.escape(t)}</span>'
            for t in topics[:3]
        )

    # Stars/forks — tampilkan hanya jika > 0 (portfolio baru semua 0, jadi hemat visual).
    stats_bits = []
    if stars:
        stats_bits.append(f'<span class="stat-pill" title="Stars">★ {stars}</span>')
    if forks:
        stats_bits.append(f'<span class="stat-pill" title="Forks">⑂ {forks}</span>')
    stats_html = " ".join(stats_bits)

    # Last-update "ago" hint (lebih jujur dari tanggal absolut).
    # Mis. "3 days ago", "2 weeks ago" — bahasa Inggris, formal tapi hangat.
    now = datetime.now(timezone.utc)
    delta = now - dt
    days = delta.days
    if days == 0:
        ago = "today"
    elif days == 1:
        ago = "yesterday"
    elif days < 7:
        ago = f"{days} days ago"
    elif days < 30:
        weeks = days // 7
        ago = f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif days < 365:
        months = days // 30
        ago = f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = days // 365
        ago = f"{years} year{'s' if years != 1 else ''} ago"

    return f'''          <article class="project-card">
            <p class="project-tag">Project · Updated {ago}</p>
            <h3 class="project-title"><a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a></h3>
            <p class="project-desc">{desc}</p>
            <div class="project-meta">
              <span class="project-lang">{lang}</span>
              {topic_tags}
              {stats_html}
            </div>
          </article>'''


def main() -> int:
    raw = os.environ.get("GITHUB_REPOS_JSON", "").strip()
    if not raw:
        print("::error::GITHUB_REPOS_JSON env var is empty", file=sys.stderr)
        return 1

    try:
        repos = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"::error::Invalid JSON: {e}", file=sys.stderr)
        return 1

    if not isinstance(repos, list):
        print("::error::Expected JSON array", file=sys.stderr)
        return 1

    # Filter & sort
    filtered = []
    for r in repos:
        if r.get("archived"):
            continue
        if r["name"] in EXCLUDED_REPOS:
            continue
        if PINNED_REPOS and r["name"] not in PINNED_REPOS:
            continue
        filtered.append(r)

    # Sort: pinned first (preserved order), then by pushed_at desc
    def sort_key(r: dict) -> tuple:
        pinned = 0 if r["name"] in PINNED_REPOS else 1
        dt = parse_pushed_at(r["pushed_at"])
        return (pinned, -dt.timestamp())

    filtered.sort(key=sort_key)
    filtered = filtered[:MAX_CARDS]

    if not filtered:
        # Tidak ada repo publik yang match. Exit 0 dengan notice supaya workflow
        # cron TIDAK gagal (semua repo sedang private).
        print("::notice::No public repos to render (all private or filtered out). Skipping index.html patch.", file=sys.stderr)
        return 0

    cards = "\n".join(render_card(r) for r in filtered)
    print(cards)
    return 0


if __name__ == "__main__":
    sys.exit(main())
