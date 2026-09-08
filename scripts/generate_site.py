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


def link_class(label: str, idx: int) -> str:
    if idx == 0:
        return "talk-link-primary"
    if idx == 1:
        return "talk-link-secondary"
    return "talk-link-extra"


def render_links(links: list[dict]) -> str:
    if not links:
        return ""
    parts = ['<div class="talk-links">']
    for idx, link in enumerate(links):
        label = esc(link.get("label", "Link"))
        url = esc(link.get("url", "#"))
        parts.append(f'<a class="{link_class(label, idx)}" href="{url}">{label}</a>')
    parts.append("</div>")
    return "".join(parts)


def sort_talks(talks: list[dict]) -> list[dict]:
    return sorted(talks, key=lambda t: (semester_key(t["semester"]), t["date"], t["speaker"], t["title"]))


def semester_order(talks: list[dict]) -> list[str]:
    seen: OrderedDict[str, None] = OrderedDict()
    for talk in sorted(talks, key=lambda t: (semester_key(t["semester"]), t["date"]), reverse=True):
        seen.setdefault(talk["semester"], None)
    return list(seen.keys())


def render_main(data: dict) -> str:
    site = data["site"]
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

    body = f'''
  <main role="main">
    <div class="container">
      <header>
        <div class="page-title-row">
          <div class="header-title-text">
            <h1>ML + Theory Seminar</h1>
            <h2>{esc(site.get('organization', 'Rensselaer Polytechnic Institute'))}</h2>
          </div>
        </div>
        <nav role="navigation" class="top-nav">
          <a href="#overview">overview</a>
          <a href="#schedule">schedule</a>
          <a href="#speakers">for speakers</a>
          <a href="#submit">submit talk</a>
        </nav>
      </header>

      <h2 id="overview">Overview</h2>
      <p class="main-lead">A weekly forum for research talks and practice for conference presentations, RQEs, and candidacies. The seminar builds cross-group awareness within the CSCI department.</p>

      <h3>Format &amp; Scope</h3>
      <ul>
        <li><strong>Format:</strong> talks, followed by Q&amp;A</li>
        <li><strong>Scope:</strong> Present an upcoming/accepted conference paper; or a relevant paper selected by the advisor; or an RQE practice talk.</li>
      </ul>

      <h2 id="schedule">Schedule, {esc(latest_semester)}</h2>
      <p class="main-lead">Monitor this space for updates as the semester fills in.</p>
      <p class="archive-note">View Fall 2025 talks <a href="mltheoryseminar_archive.html">&rarr;</a></p>

      <table>
        <thead>
          <tr><th>Date</th><th>Presenter</th><th>Title / Paper</th><th>Format</th></tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>

      <h2 id="speakers">Information for speakers</h2>
      <ul>
        <li><strong>Talk length:</strong> variable (20–40 minutes), followed by questions.</li>
        <li><strong>Good choices:</strong> your accepted/upcoming conference paper; an advisor-recommended paper; or an RQE practice talk.</li>
        <li><strong>Slides:</strong> Aim for clarity over density. Practice to hit time.</li>
        <li><strong>Q&amp;A:</strong> Expect probing questions from outside your sub-area — that’s the point!</li>
      </ul>

      <h2 id="submit">Submit a talk</h2>
      <p>Use the template below to email the organizers.</p>
      <p><strong>Subject:</strong> ML+Theory Seminar Talk — <em>Lastname, Firstname</em></p>
      <p><strong>Body:</strong> Title · Format · Abstract · Links.</p>
      <p><a href="mailto:{esc(site.get('contact', 'gittea@rpi.edu'))}">Compose email &rarr;</a></p>

      <p class="subtle">© ML + Theory Seminar · {esc(site.get('organization', 'Rensselaer Polytechnic Institute'))}</p>
    </div>
  </main>
'''
    template = read_text(DATA_DIR / "template_main.html")
    return template.replace("{{PAGE_TITLE}}", "ML + Theory Seminar | RPI").replace("{{BODY}}", body)


def render_archive(data: dict) -> str:
    site = data["site"]
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
        blocks.append(f'<div class="semester-block" id="{slugify(sem)}">')
        blocks.append(f'<div class="semester-heading">{esc(sem)}</div>')
        for talk in grouped[sem]:
            short = talk.get("short_abstract") or fallback_short_abstract(talk["abstract"])
            long_abstract = talk["abstract"]
            blocks.append(
                '<details class="talk-card">'
                '<summary class="talk-summary">'
                f'<div class="talk-headline"><span class="talk-date">{esc(compact_date(talk["date"]))}</span>'
                f'<span class="talk-speaker">{esc(talk["speaker"])}</span>'
                f'<span><strong>{esc(talk["title"])}</strong></span>'
                f'<span class="talk-format">({esc(talk["format"])})</span></div>'
                f'</summary>'
                '<div class="talk-body">'
                f'<p class="talk-abstract">{esc(short)}</p>'
                f'<details><summary>Show full abstract</summary><p class="talk-abstract">{esc(long_abstract)}</p></details>'
                f'{render_links(talk.get("links", []))}'
                '</div>'
                '</details>'
            )
        blocks.append('</div>')

    body = f'''
  <main role="main">
    <div class="container">
      <header>
        <div class="page-title-row">
          <div class="header-title-text">
            <h1>ML + Theory Seminar</h1>
            <h2>{esc(site.get('organization', 'Rensselaer Polytechnic Institute'))}</h2>
          </div>
        </div>
        <nav role="navigation" class="top-nav">
          <a href="mltheoryseminar.html">current page</a>
          <a href="#top">archive</a>
        </nav>
      </header>

      <h2 id="top">Archive</h2>
      <p>This archive groups past talks by semester. Use the links below to jump quickly to a specific semester.</p>
      <div class="semester-jumpbar">{jumps}</div>
      {''.join(blocks)}

      <p class="subtle">© ML + Theory Seminar · {esc(site.get('organization', 'Rensselaer Polytechnic Institute'))}</p>
    </div>
  </main>
'''
    template = read_text(DATA_DIR / "template_archive.html")
    return template.replace("{{PAGE_TITLE}}", "ML + Theory Seminar Archive | RPI").replace("{{BODY}}", body)


def main() -> None:
    data = load_data()
    WEBSITE_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DATA_DIR / "seminar.css", WEBSITE_DIR / "seminar.css")
    write_text(WEBSITE_DIR / "mltheoryseminar.html", render_main(data))
    write_text(WEBSITE_DIR / "mltheoryseminar_archive.html", render_archive(data))


if __name__ == "__main__":
    main()
