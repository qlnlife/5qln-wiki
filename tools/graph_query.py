#!/usr/bin/env python3
"""Graph query tool for 5QLN wiki. Explore wikilinks, backlinks, and network structure."""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
import argparse

WIKI_ROOT = Path(__file__).parent.parent / "wiki"

def extract_wikilinks(content):
    """Extract [[wikilinks]] from content."""
    return re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)

def build_graph():
    """Build directed graph: page -> [targets], and reverse index: page -> [sources]."""
    forward = defaultdict(list)
    backlinks = defaultdict(list)
    
    for md_file in WIKI_ROOT.rglob("*.md"):
        if md_file.name.startswith('.'):
            continue
        page = md_file.stem
        # Resolve relative wikilinks
        rel = md_file.relative_to(WIKI_ROOT)
        content = md_file.read_text(errors='ignore')
        targets = extract_wikilinks(content)
        for t in targets:
            forward[page].append(t)
            backlinks[t].append(page)
    
    return dict(forward), dict(backlinks)

def query_page(page, forward, backlinks, depth=1):
    """Show all links from and to a page."""
    out = []
    out.append(f"=== {page} ===")
    
    # Outgoing
    targets = forward.get(page, [])
    out.append(f"\n→ {len(targets)} outgoing: {targets if targets else '(none)'}")
    
    # Incoming
    sources = backlinks.get(page, [])
    out.append(f"\n← {len(sources)} incoming: {sources if sources else '(none)'}")
    
    return "\n".join(out)

def find_orphans(forward, backlinks):
    """Pages with no incoming links from other pages."""
    all_pages = set(forward.keys()) | set(backlinks.keys())
    orphans = []
    for p in all_pages:
        if p not in backlinks or len(backlinks[p]) == 0:
            orphans.append(p)
    return orphans

def find_bridges(forward, backlinks):
    """Pages that are critical connectors (high betweenness approximation)."""
    all_pages = set(forward.keys()) | set(backlinks.keys())
    scores = {}
    for p in all_pages:
        score = len(forward.get(p, [])) * len(backlinks.get(p, []))
        scores[p] = score
    return sorted(scores.items(), key=lambda x: -x[1])[:20]

def find_clusters(forward, backlinks):
    """Group tightly-linked pages by phase tags."""
    # Load phase metadata from files
    phase_groups = defaultdict(list)
    for md_file in WIKI_ROOT.rglob("*.md"):
        if md_file.name.startswith('.'):
            continue
        phase_match = re.search(r'^phase:\s*(\w+)', md_file.read_text(errors='ignore'), re.MULTILINE)
        if phase_match:
            phase_groups[phase_match.group(1)].append(md_file.stem)
    return dict(phase_groups)

def global_stats(forward, backlinks):
    """Summary stats."""
    all_pages = set(forward.keys()) | set(backlinks.keys())
    total_links = sum(len(v) for v in forward.values())
    out = []
    out.append(f"Pages: {len(all_pages)}")
    out.append(f"Wikilinks: {total_links}")
    out.append(f"Pages with outgoing: {sum(1 for v in forward.values() if v)}")
    out.append(f"Pages with incoming: {sum(1 for v in backlinks.values() if v)}")
    orphans = find_orphans(forward, backlinks)
    out.append(f"Orphan pages (no incoming): {len(orphans)}")
    if orphans:
        out.append(f"  → {orphans[:10]}{'...' if len(orphans) > 10 else ''}")
    return "\n".join(out)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="5QLN wiki graph query")
    parser.add_argument('--page', '-p', help='Query specific page')
    parser.add_argument('--orphans', '-o', action='store_true', help='Find orphan pages')
    parser.add_argument('--bridges', '-b', action='store_true', help='Find bridge pages')
    parser.add_argument('--clusters', '-c', action='store_true', help='Show phase clusters')
    parser.add_argument('--stats', '-s', action='store_true', help='Global stats')
    parser.add_argument('--export', '-e', help='Export graph as JSON to file')
    args = parser.parse_args()

    forward, backlinks = build_graph()

    if args.export:
        graph = {"forward": dict(forward), "backlinks": dict(backlinks)}
        Path(args.export).write_text(json.dumps(graph, indent=2))
        print(f"Exported to {args.export}")
    elif args.page:
        print(query_page(args.page, forward, backlinks))
    elif args.orphans:
        orphans = find_orphans(forward, backlinks)
        print(f"Orphan pages ({len(orphans)}):\n" + "\n".join(f"  - {o}" for o in orphans))
    elif args.bridges:
        bridges = find_bridges(forward, backlinks)
        print("Top 20 bridge pages (by link product):")
        for p, score in bridges:
            print(f"  {score:5d}  {p}")
    elif args.clusters:
        clusters = find_clusters(forward, backlinks)
        for phase, pages in sorted(clusters.items()):
            print(f"\n[{phase.upper()}] {len(pages)} pages")
            print("  " + ", ".join(pages[:8]) + ("..." if len(pages) > 8 else ""))
    elif args.stats:
        print(global_stats(forward, backlinks))
    else:
        print(global_stats(forward, backlinks))
