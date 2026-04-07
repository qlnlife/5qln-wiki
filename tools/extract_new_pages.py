#!/usr/bin/env python3
"""
extract_new_pages.py — Reads unprocessed pages from DuckDB,
extracts them as raw source documents, and marks them processed.
Run: python3 extract_new_pages.py [--limit N]
"""
import sys
import os
import json
import hashlib
import duckdb
from pathlib import Path

DB = "/home/workspace/Datasets/5qln-com/data.duckdb"
WIKI_RAW = Path("/home/workspace/5qln-wiki/raw")
WIKI_RAW_DOCS = WIKI_RAW / "documents"
PROCESSED_MARKER = WIKI_RAW / ".processed_urls.json"

def load_processed():
    if PROCESSED_MARKER.exists():
        return set(json.loads(PROCESSED_MARKER.read_text()))
    return set()

def save_processed(processed_set):
    PROCESSED_MARKER.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_MARKER.write_text(json.dumps(sorted(processed_set), ensure_ascii=False))

def url_to_slug(url):
    """Convert URL to a safe filename slug."""
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    path = url.replace("https://www.5qln.com/", "").replace("https://5qln.com/", "")
    path = path.strip("/").replace("/", "_").replace(" ", "_") or "home"
    # Clean
    keep = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
    path = "".join(c if c in keep else "_" for c in path)
    path = path[:60]
    return f"{path}_{h}.md"

def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=50)
    args = parser.parse_args()

    WIKI_RAW_DOCS.mkdir(parents=True, exist_ok=True)

    processed = load_processed()
    con = duckdb.connect(DB, read_only=True)

    rows = con.execute("""
        SELECT url, title, content, tags
        FROM pages
        WHERE content IS NOT NULL
        AND length(content) > 200
        ORDER BY depth ASC, url ASC
        LIMIT ?
    """, [args.limit]).fetchall()
    con.close()

    new_raw = []
    updated_urls = set(processed)

    for url, title, content, tags in rows:
        if url in processed:
            continue
        # Skip tag/category pages (usually thin)
        if "/tag/" in url or "/category/" in url or "/author/" in url:
            updated_urls.add(url)
            continue

        slug = url_to_slug(url)
        out_path = WIKI_RAW_DOCS / slug

        frontmatter = f"""---
title: "{title.replace('"', '\\"')}"
source: {url}
tags: [{tags}]
phase: unknown
confidence: low
---

# {title}

"""
        # Prepend frontmatter, use first 80k chars of content
        body = content[:80000] if content else ""
        out_path.write_text(frontmatter + body, encoding='utf-8')
        new_raw.append((url, title, slug))
        updated_urls.add(url)

    save_processed(updated_urls)

    print(f"Extracted {len(new_raw)} new raw documents:")
    for url, title, slug in new_raw[:10]:
        print(f"  {slug}")
        print(f"    {url}")
    if len(new_raw) > 10:
        print(f"  ... and {len(new_raw) - 10} more")

    print(f"\nTotal processed: {len(updated_urls)}")
    print(f"Raw docs in: {WIKI_RAW_DOCS}")

if __name__ == '__main__':
    run()
