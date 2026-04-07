#!/usr/bin/env python3
"""
crawl_fresh.py — Fresh crawl of 5qln.com into DuckDB.
Stores to Datasets/5qln-com/source/crawl.jsonl and updates the DuckDB pages table.
Run: python3 crawl_fresh.py [--depth N] [--max-pages N]
"""
import sys
import json
import subprocess
import os
from pathlib import Path

SCRAPER = "/home/workspace/Skills/web-scraper/scripts/scraper.py"
CRAWL_OUT = "/home/workspace/Datasets/5qln-com/source/crawl.jsonl"
DB = "/home/workspace/Datasets/5qln-com/data.duckdb"
BASE_URL = "https://www.5qln.com"
MAX_DEPTH = 3
MAX_PAGES = 200

def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--depth', type=int, default=MAX_DEPTH)
    parser.add_argument('--max-pages', type=int, default=MAX_PAGES)
    args = parser.parse_args()

    out_path = Path(CRAWL_OUT)
    if out_path.exists():
        # Resume: load existing URLs to avoid re-crawling
        existing = set()
        with open(out_path) as f:
            for line in f:
                try:
                    existing.add(json.loads(line)['url'])
                except:
                    pass
        print(f"Resuming from {len(existing)} existing pages")
    else:
        existing = set()

    # Run crawl via scraper skill
    cmd = [
        "python3", SCRAPER, "crawl", BASE_URL,
        "--depth", str(args.depth),
        "--max-pages", str(args.max_pages),
        "--output", out_path,
        "--format", "json"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        print(f"Crawl error: {result.stderr[:500]}")
        return

    # Parse and dedupe
    new_pages = []
    seen = set(existing)
    with open(out_path) as f:
        for line in f:
            try:
                page = json.loads(line)
                url = page.get('url', '')
                if url not in seen:
                    seen.add(url)
                    new_pages.append(page)
            except:
                pass

    print(f"Crawl complete. New pages: {len(new_pages)}")

    # Update DuckDB
    import duckdb
    con = duckdb.connect(DB)

    for page in new_pages:
        url = page.get('url', '')
        title = page.get('title', '')[:500]
        depth = page.get('depth', 0)
        content = page.get('content', '')[:100000]
        tags = ','.join(page.get('tags', []) or [])[:500]
        try:
            con.execute(
                "INSERT OR REPLACE INTO pages (url, title, depth, content, tags) VALUES (?, ?, ?, ?, ?)",
                [url, title, depth, content, tags]
            )
        except Exception as e:
            print(f"DB insert error for {url}: {e}")

    con.close()
    print(f"DuckDB updated with {len(new_pages)} new pages")

if __name__ == '__main__':
    run()
