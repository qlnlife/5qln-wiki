#!/usr/bin/env python3
"""
extract_new_pages.py — Pull unprocessed pages from DuckDB, write as raw source docs.
Run: python3 extract_new_pages.py [--limit N]
"""
import json, hashlib, duckdb
from pathlib import Path

DB = "/home/workspace/Datasets/5qln-com/data.duckdb"
RAW = Path("/home/workspace/5qln-wiki/raw/documents")
MARKER = RAW / ".processed.json"

SKIP_PREFIXES = ["/tag/", "/category/", "/author/", "/ghost/", "/Facebook", "/Twitter", "/LinkedIn"]

def load_processed():
    return set(json.loads(MARKER.read_text())) if MARKER.exists() else set()

def save_processed(s):
    MARKER.write_text(json.dumps(sorted(s), ensure_ascii=False))

def slug(url):
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    p = url.replace("https://www.5qln.com/", "").replace("https://5qln.com/", "").strip("/")
    p = "".join(c if c.isalnum() or c in "-_" else "_" for c in p)[:60]
    return f"{p or 'home'}_{h}.md"

def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    processed = load_processed()

    con = duckdb.connect(DB, read_only=True)
    rows = con.execute("""
        SELECT url, title, content, tags
        FROM pages
        WHERE content IS NOT NULL
          AND length(content) > 200
          AND url NOT LIKE '%/tag/%'
          AND url NOT LIKE '%/category/%'
          AND url NOT LIKE '%/author/%'
          AND url NOT LIKE '%ghost%'
        ORDER BY depth ASC, url ASC
        LIMIT ?
    """, [args.limit]).fetchall()
    con.close()

    new_urls = []
    updated = set(processed)

    for url, title, content, tags in rows:
        if url in updated:
            continue
        s = slug(url)
        (RAW / s).write_text(
            f"---\ntitle: \"{title.replace(chr(34), chr(92)+chr(34))}\"\nsource: {url}\ntags: [{tags or 'untagged'}]\nphase: unknown\nconfidence: low\n---\n\n# {title}\n\n" + (content or "")[:80000],
            encoding="utf-8"
        )
        new_urls.append((url, title, s))
        updated.add(url)

    save_processed(updated)
    print(f"Extracted {len(new_urls)} new raw docs:")
    for u, t, s in new_urls[:10]:
        print(f"  {s}")
    if len(new_urls) > 10:
        print(f"  ... +{len(new_urls)-10} more")
    print(f"\nTotal processed: {len(updated)}")

if __name__ == "__main__":
    run()
