#!/usr/bin/env python3
"""One-off: Squarespace WXR export -> Zensical markdown.

Reads the WordPress-format XML, keeps the real content (23 project posts +
real pages), drops Squarespace placeholder posts (press/reviews) and the
duplicate Home. Converts each item's HTML to Markdown via markdownify,
turns video/audio iframes into embeds/links, and rewrites Squarespace CDN
image URLs to local ``assets/`` paths. Emits an ``image_urls.tsv`` manifest
(url<TAB>filename) for the downloader step.
"""
from __future__ import annotations
import html
import os
import re
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

from markdownify import markdownify as md

NS = {
    "wp": "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
}
ROOT = Path(__file__).resolve().parent.parent
XML = Path(os.environ.get(
    "SQSP_XML",
    "/home/harpo/Downloads/harpo.me/Squarespace-Wordpress-Export-07-12-2026.xml",
))
DOCS = ROOT / "docs"

# Slug -> clean slug overrides (Squarespace hash slugs).
SLUG_OVERRIDE = {"s2ig08ghl4kngswm15jdotj0z8eq9g": "dellarte-productions"}

# Pages to migrate: squarespace name -> output md path (relative to docs/).
PAGES = {
    "harpo": "about.md",
    "acting": "acting.md",
    "cesarrubin": "cesarrubin.md",
    "oompah-kings": "oompah-kings.md",
    "events": "events.md",
    "hire": "hire.md",
    "sponsor": "sponsor.md",
    "contact": "contact.md",
}

# Project slug -> tags (groupings).
PROJECT_TAGS = {
    "5-fun-facts-about-me": ["personal"],
    "adonai": ["music"],
    "corona-chords": ["music"],
    "greater-tuna": ["theater"],
    "harpo-amp-holophonor-home": ["music", "tech"],
    "harpo-amp-the-holophonor-backyard-party": ["music"],
    "holophonor": ["tech", "music"],
    "ira": ["tech"],
    "launchchess": ["tech"],
    "pre-visualization": ["theater", "tech"],
    "projection-design": ["theater", "tech"],
    "quaternion-media": ["tech"],
    "ready-set-jazz": ["music"],
    "ready-set-jazz-backyard-reunion": ["music"],
    "rocky-horror-2013": ["theater"],
    "dellarte-productions": ["theater"],
    "selected-reel": ["reel"],
    "socially-distanced-backyard-party": ["music"],
    "sound-reactive-el-wire-coat": ["tech"],
    "the-apple-strudelers": ["music"],
    "the-elaine-lord-band": ["music"],
    "the-oompah-kings-oktoberfest-2021": ["music"],
    "toccata-and-fugue-halloween-light-show": ["tech"],
}

image_map: dict[str, str] = {}   # cdn_url (no query) -> local filename
_used_names: dict[str, str] = {}  # filename -> source url (collision guard)


def localize(url: str) -> str:
    """Register a CDN image URL, return local ``assets/<file>`` path."""
    base = url.split("?")[0]
    name = urllib.parse.unquote(os.path.basename(base))
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name) or "image"
    if name in _used_names and _used_names[name] != base:
        stem, ext = os.path.splitext(name)
        name = f"{stem}-{abs(hash(base)) % 100000}{ext}"
    _used_names[name] = base
    image_map[base] = name
    return f"assets/{name}"


def embed(iframe: str) -> str:
    """Turn an <iframe> into a Markdown embed/link."""
    m = re.search(r'src="([^"]+)"', iframe)
    if not m:
        return ""
    src = m.group(1)
    if src.startswith("//"):
        src = "https:" + src
    title_m = re.search(r'title="([^"]*)"', iframe)
    title = html.unescape(title_m.group(1)) if title_m else ""

    # embedly wrapper: real target is the `url` query param.
    if "embedly" in src:
        q = urllib.parse.urlparse(src).query
        params = urllib.parse.parse_qs(q)
        src = params.get("url", params.get("src", [src]))[0]

    yt = re.search(r"(?:youtube\.com|youtu\.be).*?[?&/](?:v=|embed/|watch\?v=)?([\w-]{11})", src)
    is_playlist = "list=" in src and "watch?v=" not in src and "/embed/" not in src
    if "youtube" in src and yt and not is_playlist:
        vid = yt.group(1)
        return (f'<div class="video"><iframe src="https://www.youtube.com/embed/{vid}"'
                f' frameborder="0" allowfullscreen></iframe></div>')
    vim = re.search(r"vimeo\.com/(?:video/)?(\d+)", src)
    if vim:
        return (f'<div class="video"><iframe src="https://player.vimeo.com/video/{vim.group(1)}"'
                f' frameborder="0" allowfullscreen></iframe></div>')
    label = title or ("YouTube playlist" if is_playlist else "Open media")
    if "youtube" in src:
        label = title if title and title != "YouTube embed" else "▶ Watch on YouTube"
    elif "soundcloud" in src:
        label = "♪ Listen on SoundCloud"
    return f"[{label}]({src})"


def preprocess(content: str) -> str:
    """Replace iframes with markdown-safe tokens; strip [caption] shortcodes."""
    content = re.sub(r"<iframe\b.*?</iframe>", lambda m: f"\n\n{embed(m.group(0))}\n\n",
                     content, flags=re.S)
    content = re.sub(r"\[caption[^\]]*\]", "", content)
    content = content.replace("[/caption]", "")
    return content


def to_markdown(content: str) -> str:
    body = md(preprocess(content), heading_style="ATX", bullets="-", strip=["style"])
    # rewrite CDN image urls -> local asset paths
    def repl(m):
        return localize(m.group(0))
    body = re.sub(r"https?://images\.squarespace-cdn\.com[^\s\"')]+", repl, body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body


def frontmatter(title: str, date: str = "", tags: list[str] | None = None) -> str:
    lines = ["---", f"title: {title!r}"]
    if date:
        lines.append(f"date: {date[:10]}")
    if tags:
        lines.append("tags:")
        lines += [f"  - {t}" for t in tags]
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def main() -> None:
    tree = ET.parse(XML)
    (DOCS / "projects").mkdir(parents=True, exist_ok=True)
    written = 0
    for it in tree.getroot().iter("item"):
        pt = it.findtext("wp:post_type", "", NS)
        name = it.findtext("wp:post_name", "", NS)
        link = it.findtext("link", "") or ""
        title = html.unescape(it.findtext("title", "") or "")
        content = it.findtext("content:encoded", "", NS) or ""
        date = it.findtext("wp:post_date", "", NS) or ""

        if pt == "post" and link.startswith("/projects/"):
            slug = SLUG_OVERRIDE.get(name, name)
            out = DOCS / "projects" / f"{slug}.md"
            fm = frontmatter(title, date, PROJECT_TAGS.get(slug))
        elif pt == "page" and name in PAGES:
            out = DOCS / PAGES[name]
            fm = frontmatter(title)
        else:
            continue  # drop placeholders, home, home-copy, attachments

        out.write_text(fm + to_markdown(content) + "\n", encoding="utf-8")
        written += 1

    manifest = ROOT / "image_urls.tsv"
    with manifest.open("w", encoding="utf-8") as f:
        for url, fname in sorted(image_map.items()):
            f.write(f"{url}\t{fname}\n")
    print(f"wrote {written} markdown files, {len(image_map)} unique images -> {manifest}")


if __name__ == "__main__":
    main()
