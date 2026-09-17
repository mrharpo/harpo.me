#!/usr/bin/env python3
"""Download images from the image_urls.tsv manifest to docs/assets/."""
import sys
import urllib.request
import urllib.error
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent / "image_urls.tsv"
ASSETS = Path(__file__).resolve().parent.parent / "docs" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

def main() -> None:
    with open(MANIFEST, encoding="utf-8") as f:
        lines = f.read().strip().split("\n")
    
    ok, skip, fail = 0, 0, 0
    for line in lines:
        if not line.strip():
            continue
        url, fname = line.split("\t", 1)
        path = ASSETS / fname
        if path.exists():
            skip += 1
            continue
        try:
            urllib.request.urlretrieve(url, path)
            ok += 1
            if ok % 10 == 0:
                print(f"downloaded {ok}...", file=sys.stderr)
        except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
            print(f"FAIL {url}: {e}", file=sys.stderr)
            fail += 1
    print(f"ok={ok}, skip={skip}, fail={fail}")

if __name__ == "__main__":
    main()
