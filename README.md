# ML Theory Seminar Website

This repository manages the ML + Theory Seminar website as a small static site.
The goal is to keep all seminar history in one place, make local browsing easy,
and keep deployment to the RPI web server simple and predictable.

## Purpose

- Store all current and historical seminar talks in a single data file.
- Generate the public website into `website/`.
- Keep the main seminar page and the archive page separate but consistent.
- Make local viewing as simple as opening the generated HTML files in a browser.
- Deploy only the generated website files with `rsync`.

## Repository Layout

```text
mltheory_seminar/
├── data/
│   ├── talks.json
│   ├── template_main.html
│   ├── template_archive.html
│   └── seminar.css
├── scripts/
│   ├── generate_site.py
│   └── push-website.sh
└── website/
    ├── mltheoryseminar.html
    ├── mltheoryseminar_archive.html
    └── seminar.css
```

## Data Model

All talk information lives in `data/talks.json`.

Each talk entry should include:

- `semester`
- `date`
- `speaker`
- `title`
- `format`
- `abstract`
- `short_abstract`
- `links`

The generator also copies the shared stylesheet from `data/seminar.css` into
`website/seminar.css`.

Both `abstract` and `short_abstract` may contain math in `\(...\)` format.
The site uses KaTeX-style rendering, so this format should be preserved in the
source data.

`short_abstract` is the preferred field for the archive page. If it is missing,
the generator can fall back to a truncated version of `abstract`.

## Website Structure

- `mltheoryseminar.html` is the main seminar page.
- `mltheoryseminar_archive.html` is the archive page.
- `seminar.css` holds the shared styling.

The archive page groups talks by semester and includes jump links at the top so
you can quickly move to a specific semester.

For archive entries, the short abstract should show by default and the full
abstract should be expandable on demand.

## Editing Workflow

1. Edit `data/talks.json` to add or update talks.
2. Edit the templates or generator if the page structure changes.
3. Run the site generator to refresh `website/`.
4. Open the HTML files in `website/` directly in your browser for local review.

## Deployment

Deployment should use `rsync` in the same style as the randomized-algorithms
course repo: sync the `website/` directory to the remote web root with
`--delete`, so the remote copy stays aligned with the generated site.

Remote target:

```bash
REMOTE="gittea@linux.cs.rpi.edu:/cs/gittea/public.html/old-site/teaching/mltheoryseminar/"
```

The deploy script should only publish the generated website files in `website/`.

## Style

- Main page: follow the style of the current seminar page.
- Archive page: follow the style of the Fall 2025 archive page.

## Notes

- This repository intentionally does not keep separate semester websites.
- Old semester URLs are not part of this repo’s publishing workflow.
- Keep the source data authoritative and regenerate the website from it.
