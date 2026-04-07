#!/usr/bin/env python3
"""
state_manager.py — Tracks processed URLs and wiki page state.
Run: python3 state_manager.py --status
"""
import json, sys
from pathlib import Path

WIKI_RAW_DOCS = Path("/home/workspace/5qln-wiki/raw/documents")
PROCESSED_FILE = WIKI_RAW_DOCS / ".processed.json"
SKIP_FILE = WIKI_RAW_DOCS / ".skip.json"

def load_set(path):
    if path.exists():
        return set(json.loads(path.read_text()))
    return set()

def save_set(path, s):
    path.write_text(json.dumps(sorted(s), ensure_ascii=False), encoding="utf-8")

def status():
    processed = load_set(PROCESSED_FILE)
    skip = load_set(SKIP_FILE)
    raw_files = list(WIKI_RAW_DOCS.glob("*.md"))
    print(f"Raw docs: {len(raw_files)}")
    print(f"Processed: {len(processed)}")
    print(f"Skipped: {len(skip)}")
    print(f"Remaining: {len(raw_files) - len(processed) - len(skip)}")
    if "--detail" in sys.argv:
        print("\nSkipped URLs:")
        for u in sorted(skip):
            print(f"  skip: {u}")

if __name__ == "__main__":
    status()
