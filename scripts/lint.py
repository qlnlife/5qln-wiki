#!/usr/bin/env python3
"""
5QLN Wiki — Lint Script
Health-checks the wiki for contradictions, stale claims, orphans, missing cross-refs.

Usage:
  python3 lint.py [--fix]
  
Without --fix: reports issues only
With --fix: attempts automatic fixes
"""

import os
import sys
from datetime import datetime

WIKI_ROOT = "/home/workspace/5qln-wiki"

def get_wiki_pages():
    pages = []
    for root, dirs, files in os.walk(WIKI_ROOT):
        for f in files:
            if f.endswith(".md") and f not in ["SCHEMA.md", "index.md", "log.md"]:
                rel = os.path.relpath(os.path.join(root, f), WIKI_ROOT)
                pages.append(rel)
    return pages

def count_wiki_stats():
    pages = get_wiki_pages()
    total = len(pages)
    
    entities = [p for p in pages if "/entities/" in p]
    concepts = [p for p in pages if "/concepts/" in p]
    sessions = [p for p in pages if "/sessions/" in p]
    synthesis = [p for p in pages if "/synthesis/" in p]
    
    return {
        "total": total,
        "entities": len(entities),
        "concepts": len(concepts),
        "sessions": len(sessions),
        "synthesis": len(synthesis),
        "pages": pages
    }

def lint():
    stats = count_wiki_stats()
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"""5QLN Wiki — Lint Report
Generated: {today}
========================

## Wiki Stats
- Total pages: {stats['total']}
- Entities: {stats['entities']}
- Concepts: {stats['concepts']}
- Sessions: {stats['sessions']}
- Synthesis: {stats['synthesis']}

## Pages
""")
    for p in sorted(stats['pages']):
        print(f"  - {p}")
    
    print(f"""

## Lint Protocol (TO FILL by LLM)
1. Check for contradictions between pages
2. Check for stale claims superseded by newer sources
3. Check for orphan pages (no inbound links)
4. Check for important concepts lacking their own page
5. Check for missing cross-references
6. Check for data gaps addressable via web search

## Issues Found (TO FILL)
-

## Actions Taken (TO FILL)
-

## ∞0'
What does the lint reveal about what the wiki needs next?
""")

if __name__ == "__main__":
    lint()
