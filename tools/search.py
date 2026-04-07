#!/usr/bin/env python3
"""
5QLN Wiki Search — A simple search engine for the wiki.

Usage:
    python search.py "query terms"
    python search.py --index              # Show the index
    python search.py --log                # Show recent log entries
    python search.py --lint               # Quick health check
    python search.py --stats              # Wiki statistics

This is intentionally simple. At small-to-medium scale (~100-500 pages),
BM25-style keyword search over markdown files works surprisingly well.
When the wiki outgrows this, plug in qmd or a proper search engine.
"""

import os
import sys
import re
import math
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

WIKI_DIR = Path(__file__).parent.parent / "wiki"
RAW_DIR = Path(__file__).parent.parent / "raw"


def tokenize(text: str) -> list[str]:
    """Simple tokenizer: lowercase, split on non-alphanumeric."""
    return re.findall(r'[a-z0-9∞αφδ]+', text.lower())


def load_pages() -> dict[str, str]:
    """Load all markdown files from the wiki directory."""
    pages = {}
    for path in WIKI_DIR.rglob("*.md"):
        rel = path.relative_to(WIKI_DIR)
        try:
            pages[str(rel)] = path.read_text(encoding='utf-8')
        except Exception:
            pass
    return pages


def strip_hash(filename: str) -> str:
    """Strip trailing _hash.md suffix to get the canonical page name."""
    import re
    return re.sub(r'_[a-f0-9]{8}\.md$', '.md', filename)


def bm25_search(query: str, pages: dict[str, str], k: int = 10) -> list[tuple[str, float]]:
    """BM25 ranking over wiki pages."""
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    # Build document frequency
    doc_tokens = {}
    doc_lengths = {}
    df = Counter()

    for path, content in pages.items():
        tokens = tokenize(content)
        doc_tokens[path] = Counter(tokens)
        doc_lengths[path] = len(tokens)
        for t in set(tokens):
            df[t] += 1

    N = len(pages)
    avg_dl = sum(doc_lengths.values()) / max(N, 1)

    # BM25 parameters
    k1 = 1.5
    b = 0.75

    scores = {}
    for path in pages:
        score = 0.0
        dl = doc_lengths[path]
        tf_map = doc_tokens[path]

        for qt in query_tokens:
            tf = tf_map.get(qt, 0)
            if tf == 0:
                continue
            idf = math.log((N - df.get(qt, 0) + 0.5) / (df.get(qt, 0) + 0.5) + 1)
            tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))
            score += idf * tf_norm

        if score > 0:
            scores[path] = score

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    return ranked[:k]


def extract_title(content: str) -> str:
    """Extract the first heading from markdown content."""
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
    return "(untitled)"


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter if present."""
    if not content.startswith('---'):
        return {}
    end = content.find('---', 3)
    if end == -1:
        return {}
    fm = {}
    for line in content[3:end].strip().split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip()
    return fm


def show_search(query: str):
    """Search the wiki and display results."""
    pages = load_pages()
    results = bm25_search(query, pages)

    if not results:
        print(f"No results for: {query}")
        return

    print(f"\n🔍 Results for: {query}\n")
    for i, (path, score) in enumerate(results, 1):
        content = pages[path]
        title = extract_title(content)
        fm = extract_frontmatter(content)
        phase = fm.get('phase', '')
        ptype = fm.get('type', '')

        # Extract snippet
        query_tokens = set(tokenize(query))
        lines = content.split('\n')
        snippet = ""
        for line in lines:
            line_tokens = set(tokenize(line))
            if query_tokens & line_tokens and not line.startswith('---') and not line.startswith('#'):
                snippet = line.strip()[:120]
                break

        phase_badge = f" [{phase}]" if phase else ""
        type_badge = f" ({ptype})" if ptype else ""
        print(f"  {i}. {title}{type_badge}{phase_badge}")
        print(f"     📄 wiki/{path}  (score: {score:.2f})")
        if snippet:
            print(f"     {snippet}...")
        print()


def show_index():
    """Display the wiki index."""
    index_path = WIKI_DIR / "index.md"
    if index_path.exists():
        print(index_path.read_text(encoding='utf-8'))
    else:
        print("No index.md found.")


def show_log(n: int = 10):
    """Show recent log entries."""
    log_path = WIKI_DIR / "log.md"
    if not log_path.exists():
        print("No log.md found.")
        return

    content = log_path.read_text(encoding='utf-8')
    entries = re.findall(r'^## \[.*$', content, re.MULTILINE)
    recent = entries[-n:] if len(entries) > n else entries

    print(f"\n📋 Recent log entries ({len(recent)} of {len(entries)}):\n")
    for entry in recent:
        print(f"  {entry}")
    print()


def show_stats():
    """Wiki statistics."""
    pages = load_pages()
    total_words = sum(len(tokenize(c)) for c in pages.values())

    # Count by type
    types = Counter()
    phases = Counter()
    for path, content in pages.items():
        fm = extract_frontmatter(content)
        types[fm.get('type', 'untyped')] += 1
        if fm.get('phase'):
            phases[fm.get('phase')] += 1

    # Count raw sources
    raw_count = sum(1 for _ in RAW_DIR.rglob("*") if _.is_file()) if RAW_DIR.exists() else 0

    # Wikilinks — build lookup set with hash-stripped paths for hashed filenames
    all_links = set()
    broken_links = set()
    # Strip hash suffixes to get canonical names (01-introduction-to-the-nunc-protocol_4cb3115c.md → concepts/01-introduction-to-the-nunc-protocol.md)
    canonical_pages = set()
    for p in pages:
        import re
        canonical = re.sub(r'(_[a-f0-9]{8})(\.md)$', r'\2', p)
        canonical_pages.add(canonical)
    for content in pages.values():
        links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
        for link in links:
            all_links.add(link)
            candidates = [
                f"{link}.md",
                f"concepts/{link}.md",
                f"entities/{link}.md",
                f"sources/{link}.md",
                f"outputs/{link}.md",
            ]
            if not any(c in pages for c in candidates) and not any(c in canonical_pages for c in candidates):
                broken_links.add(link)

    print(f"\n📊 5QLN Wiki Statistics\n")
    print(f"  Wiki pages:     {len(pages)}")
    print(f"  Total words:    ~{total_words:,}")
    print(f"  Raw sources:    {raw_count}")
    print(f"  Wikilinks:      {len(all_links)}")
    print(f"  Broken links:   {len(broken_links)}")
    print()

    if types:
        print("  By type:")
        for t, n in types.most_common():
            print(f"    {t}: {n}")
        print()

    if phases:
        print("  By phase:")
        for p in ['S', 'G', 'Q', 'P', 'V', 'meta']:
            if p in phases:
                print(f"    {p}: {phases[p]}")
        print()

    if broken_links:
        print("  ⚠️  Broken wikilinks:")
        for link in sorted(broken_links)[:10]:
            print(f"    [[{link}]]")
        if len(broken_links) > 10:
            print(f"    ... and {len(broken_links) - 10} more")
        print()


def quick_lint():
    """Quick health check of the wiki."""
    pages = load_pages()

    print(f"\n🔧 Wiki Lint Report\n")

    issues = []

    # Check for pages without frontmatter
    no_fm = [p for p, c in pages.items() if not c.startswith('---')]
    if no_fm:
        issues.append(f"  ⚠️  {len(no_fm)} pages without frontmatter: {', '.join(no_fm[:5])}")

    # Build canonical pages for link checking
    canonical_pages = set()
    for p in pages:
        canonical = re.sub(r'(_[a-f0-9]{8})(\.md)$', r'\2', p)
        canonical_pages.add(canonical)

    # Check for broken wikilinks
    broken = set()
    for content in pages.values():
        links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
        for link in links:
            candidates = [
                f"{link}.md", f"concepts/{link}.md", f"entities/{link}.md",
                f"sources/{link}.md", f"outputs/{link}.md",
            ]
            if not any(c in pages for c in candidates) and not any(c in canonical_pages for c in candidates):
                broken.add(link)
    if broken:
        issues.append(f"  ⚠️  {len(broken)} broken wikilinks: {', '.join(sorted(broken)[:5])}")

    # Check for orphan pages (no inbound links)
    all_links = set()
    for content in pages.values():
        all_links.update(re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content))

    orphans = []
    for path in pages:
        name = Path(path).stem
        if name not in ['index', 'log', 'overview'] and name not in all_links:
            orphans.append(path)
    if orphans:
        issues.append(f"  ⚠️  {len(orphans)} orphan pages (no inbound links): {', '.join(orphans[:5])}")

    # Check for contradiction markers
    contradictions = 0
    for content in pages.values():
        contradictions += content.count('⚠️ CONTRADICTION')
    if contradictions:
        issues.append(f"  ⚠️  {contradictions} unresolved contradictions in the wiki")

    # Check phase coverage
    phases_present = set()
    for content in pages.values():
        fm = extract_frontmatter(content)
        if fm.get('phase') in ['S', 'G', 'Q', 'P', 'V']:
            phases_present.add(fm['phase'])
    missing_phases = {'S', 'G', 'Q', 'P', 'V'} - phases_present
    if missing_phases:
        issues.append(f"  ℹ️  Phases not yet covered: {', '.join(sorted(missing_phases))}")

    if issues:
        for issue in issues:
            print(issue)
    else:
        print("  ✅ No issues found.")

    print(f"\n  Total pages: {len(pages)}")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py <query>")
        print("       python search.py --index | --log | --stats | --lint")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "--index":
        show_index()
    elif arg == "--log":
        show_log()
    elif arg == "--stats":
        show_stats()
    elif arg == "--lint":
        quick_lint()
    else:
        query = " ".join(sys.argv[1:])
        show_search(query)
