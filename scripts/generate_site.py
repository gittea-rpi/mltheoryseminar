#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import shutil
from collections import OrderedDict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
WEBSITE_DIR = ROOT / "website"
LOGO_NAME = "ml-theory-seminar-logo.png"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_data() -> dict:
    with (DATA_DIR / "talks.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def compact_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%b %-d") if "% -d" else dt.strftime("%b %d")


def semester_key(semester: str) -> tuple[int, int, str]:
    match = re.match(r"^(Spring|Summer|Fall)\s+(\d{4})$", semester)
    if not match:
        return (0, 0, semester)
    term, year = match.group(1), int(match.group(2))
    term_rank = {"Spring": 1, "Summer": 2, "Fall": 3}[term]
    return (year, term_rank, semester)


def fallback_short_abstract(text: str, max_chars: int = 260) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    boundary = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "), cut.rfind("; "))
    if boundary >= int(max_chars * 0.5):
        cut = cut[: boundary + 1]
    else:
        cut = cut.rstrip()
    return cut.rstrip() + "…"


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def render_links(links: list[dict]) -> str:
    if not links:
        return ""
    parts = ['<p class="subtle">Links: ']
    for idx, link in enumerate(links):
        label = esc(link.get("label", "Link"))
        url = esc(link.get("url", "#"))
        if idx:
            parts.append(" · ")
        parts.append(f'<a href="{url}">{label}</a>')
    parts.append("</p>")
    return "".join(parts)


def sort_talks(talks: list[dict]) -> list[dict]:
    return sorted(talks, key=lambda t: (semester_key(t["semester"]), t["date"], t["speaker"], t["title"]))


def semester_order(talks: list[dict]) -> list[str]:
    seen: OrderedDict[str, None] = OrderedDict()
    for talk in sorted(talks, key=lambda t: (semester_key(t["semester"]), t["date"]), reverse=True):
        seen.setdefault(talk["semester"], None)
    return list(seen.keys())


def render_main(data: dict) -> str:
    talks = [t for t in sort_talks(data["talks"])]
    latest_semester = semester_order(talks)[0]
    current = [t for t in talks if t["semester"] == latest_semester]

    rows = []
    for talk in current:
        links = render_links(talk.get('links', []))
        rows.append(
            "<tr>"
            f"<td>{esc(compact_date(talk['date']))}</td>"
            f"<td>{esc(talk['speaker'])}</td>"
            f"<td><strong>{esc(talk['title'])}</strong><br><span class='subtle'>{esc(talk['format'])}</span><br><br><em>Abstract:</em> {esc(talk['abstract'])}{links}</td>"
            f"<td><span class='tag'>{esc(talk.get('duration', '20m + Q&A'))}</span></td>"
            "</tr>"
        )

    template = read_text(DATA_DIR / "template_main.html")
    return (
        template.replace("{{PAGE_TITLE}}", "ML + Theory Seminar | RPI")
        .replace("{{LOGO_SRC}}", LOGO_NAME)
        .replace("{{CURRENT_SEMESTER}}", esc(latest_semester))
        .replace("{{TALK_ROWS}}", "".join(rows))
    )


def render_archive(data: dict) -> str:
    talks = sort_talks(data["talks"])
    current_semester = semester_order(talks)[0]
    old_talks = [t for t in talks if t["semester"] != current_semester]
    semesters = semester_order(old_talks)
    grouped: OrderedDict[str, list[dict]] = OrderedDict((s, []) for s in semesters)
    for talk in old_talks:
        grouped[talk["semester"]].append(talk)

    jumps = ''.join(f'<a href="#{slugify(sem)}">{esc(sem)}</a>' for sem in semesters)
    blocks = []
    for sem in semesters:
        blocks.append(f'<section class="archive-semester" id="{slugify(sem)}">')
        blocks.append(f'<h3 class="archive-semester-title">{esc(sem)}</h3>')
        blocks.append('<div class="archive-list">')
        for talk in grouped[sem]:
            short = talk.get("short_abstract") or fallback_short_abstract(talk["abstract"])
            long_abstract = talk["abstract"]
            blocks.append(
                '<article class="archive-talk">'
                f'<div class="archive-date">{esc(compact_date(talk["date"]))}</div>'
                '<div class="archive-main">'
                f'<h4 class="archive-title">{esc(talk["title"])}</h4>'
                '<div class="archive-meta">'
                f'<span class="archive-speaker">{esc(talk["speaker"])}</span>'
                '<span aria-hidden="true" class="archive-meta-sep">·</span>'
                f'<span class="archive-format">{esc(talk["format"])}</span>'
                '</div>'
                f'<p class="archive-summary">{esc(short)}</p>'
                f'<details class="archive-abstract"><summary>Abstract</summary><div class="archive-abstract-body"><p>{esc(long_abstract)}</p></div></details>'
                f'{render_links(talk.get("links", []))}'
                '</div>'
                '</article>'
            )
        blocks.append('</div>')
        blocks.append('</section>')

    template = read_text(DATA_DIR / "template_archive.html")
    return (
        template.replace("{{PAGE_TITLE}}", "ML + Theory Seminar Archive | RPI")
        .replace("{{LOGO_SRC}}", LOGO_NAME)
        .replace("{{SEMESTER_JUMPS}}", jumps)
        .replace("{{ARCHIVE_BLOCKS}}", "".join(blocks))
    )


def main() -> None:
    data = load_data()
    WEBSITE_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DATA_DIR / "seminar.css", WEBSITE_DIR / "seminar.css")
    shutil.copy2(DATA_DIR / LOGO_NAME, WEBSITE_DIR / LOGO_NAME)
    write_text(WEBSITE_DIR / "mltheoryseminar.html", render_main(data))
    write_text(WEBSITE_DIR / "mltheoryseminar_archive.html", render_archive(data))


if __name__ == "__main__":
    main()
