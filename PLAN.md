# Migrate harpo.me from Squarespace XML → Zensical

## Context
The site currently lives on Squarespace. A WordPress-format (WXR) export exists at
`~/Downloads/harpo.me/Squarespace-Wordpress-Export-07-12-2026.xml`. This repo
(`Migrate-to-zensical`) is a fresh Zensical project (only `pyproject.toml` pinning
`zensical>=0.0.62`, an empty `assets/` dir). Goal: turn the export into a working
Zensical static site — `zensical.toml` config + `docs/*.md` + localized images.

## What's in the export (70 items)
- **10 `page` items** — heavy Squarespace layout markup (nav, newsletter forms,
  event widgets). Mostly chrome, little prose. Includes a `Home (Copy)` duplicate.
  Real ones: Home, Events, About me (`/harpo`), hire, acting, sponsor, contact,
  Cesar & Rubin, OomPah Kings.
- **34 `post` items**:
  - **23 `projects/*`** — the REAL content (bands, shows, tech projects), clean
    `sqs-html-content` HTML: headings, paragraphs, image galleries, YouTube iframes.
  - **6 `press/*`** — Lorem ipsum placeholders (Squarespace demo). → **drop**
  - **5 `reviews/*`** — "It all begins with an idea…" demo placeholders + 1 empty
    draft. → **drop**
- **26 `attachment` items** — image records (not pages). → used for image mapping only.

## Images
- Content references **143 unique** Squarespace CDN images (572 raw refs).
- `~/Downloads/harpo.me/assets/` already has 22 downloaded; not the full set.
- Need to download the rest, store under `docs/assets/`, and rewrite `<img src>`
  CDN URLs → local relative paths.

## Decisions (confirmed)
- Drop `press/*`, `reviews/*` placeholders and the `Home (Copy)` duplicate.
- Fresh, simple `docs/index.md` landing page (do not port Squarespace Home widgets).
- **Include drafts** (LaunchChess, Pre-visualization) as normal published pages.
- **Flat projects list** in nav; use the **`tags` plugin** for groupings
  (music / theater / tech / etc.) via `tags:` frontmatter + a `docs/tags.md` index.
- Download all 143 referenced images and localize.
- Use **`markdownify`** for HTML→Markdown conversion (add as a dependency).

## Approach
1. **Config**: base `zensical.toml` on the bootstrap; set `site_name` ("Harpo!"),
   `site_url = https://harpo.me`, author, hand-written flat `nav`, enable the
   `tags` plugin (`tags_file = tags.md`). Point theme assets at `docs/assets/`.
2. **Content selection**: migrate the 23 `projects/*` posts + real pages
   (About `/harpo`, contact, hire, sponsor, acting, events, Cesar & Rubin,
   OomPah Kings). Drop placeholders + duplicate.
3. **HTML→Markdown converter** `scripts/convert.py` (run once): parse the XML with
   `xml.etree`, pull `content:encoded` per kept item, pre-clean Squarespace
   wrappers (`sqs-html-content`, `image-gallery-wrapper`, `[caption]` shortcodes),
   convert `iframe` embedly/YouTube → a plain YouTube link/embed, then run
   `markdownify` for the rest. Emit `docs/projects/<slug>.md` (+ page files) with
   YAML frontmatter: `title`, `date`, `tags`, `draft` note if applicable.
4. **Images**: collect all CDN URLs from kept content, download to `docs/assets/`
   (reuse the 22 already fetched where filenames match), rewrite `<img src>` →
   relative `assets/...` paths. Dedupe by CDN filename.
5. **Landing page**: hand-write `docs/index.md` — short intro
   ("musician, technician, designer") + links into Projects/About/Contact.
6. **Tags index**: `docs/tags.md` with the tags-listing directive.
7. **Verify** with `zensical build` / `serve`.

## Files to create/modify
- `zensical.toml` (new, repo root)
- `docs/index.md`, `docs/projects/*.md`, `docs/about.md`, `docs/contact.md`, etc.
- `docs/assets/*` (images)
- `scripts/convert.py` (one-off migration script, kept for re-runs)

## Reuse
- Zensical bootstrap config: `.venv/.../zensical/bootstrap/zensical.toml`
- Bootstrap markdown examples: `.venv/.../zensical/bootstrap/docs/`
- 22 pre-downloaded images: `~/Downloads/harpo.me/assets/`
- `~/Downloads/squarespace_image_downloader/image_downloader.py` (reference)
- Python stdlib `xml.etree`/`html`/`urllib` + `markdownify` (new dep).
- Zensical `tags` plugin (Material-compatible) — confirmed supported in config.py.

## Steps
- [x] Add `markdownify` to `pyproject.toml` deps
- [x] Write `zensical.toml` (nav, tags plugin, site metadata)
- [x] Write & run `scripts/convert.py` (XML → `docs/projects/*.md` + page files)
- [x] Download + localize all 143 images into `docs/assets/`, rewrite refs
- [x] Write `docs/index.md` landing page + `docs/tags.md` index
- [x] `uv run zensical build` and fix issues

## Verification
- `uv run zensical build` completes with no errors
- `uv run zensical serve` → spot-check project pages, images load, nav works
