#!/usr/bin/env python3
"""
validate_wiki.py — C1 validation checks on all wiki pages.
Run: python3 validate_wiki.py
"""
import re, sys
from pathlib import Path

WIKI = Path("/home/workspace/5qln-wiki/wiki")
# L1-L4 in both ASCII and Unicode superscript forms
CORRUPTION_CODES = ["L1", "L2", "L3", "L4", "V\u2205"]
CORRUPTION_VARIANTS = {
    "L1": ["L1", "L\u00b9"],
    "L2": ["L2", "L\u00b2"],
    "L3": ["L3", "L\u00b3"],
    "L4": ["L4", "L\u2074"],
    "V\u2205": ["V\u2205", "V\u2205"],
}
PHASES = ["S", "G", "Q", "P", "V"]
KNOWN_MISSING = {"attention-router", "holographic-sub-phases", "echo-system",
                 "n-unc-protocol", "ecio-protocol", "harp", "fcf", "pentagon-fractal-shell",
                 "n-unc-protocol-as-truth-lens-a-live-validation-test",
                 "01-introduction-to-the-nunc-protocol"}

def parse_fm(content):
    fm = {}
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            for line in content[3:end].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip()
    return fm

def has_corruption_code(content, code):
    variants = CORRUPTION_VARIANTS.get(code, [code])
    return any(v in content for v in variants)

def validate_page(path):
    content = path.read_text(encoding="utf-8")
    issues = []
    fm = parse_fm(content)
    is_concept = fm.get("type") == "concept"
    phase = fm.get("phase", "")
    # Constitutional check (high-confidence concept pages)
    if is_concept and fm.get("confidence") == "high":
        if "H=\u221e0" not in content and "H = \u221e0" not in content:
            issues.append("missing_constitutional:H=\u221e0|A=K")
    # Corruption codes completeness
    if "corruption" in path.stem.lower() and is_concept:
        for code in CORRUPTION_CODES:
            if not has_corruption_code(content, code):
                issues.append(f"missing_corruption_code:{code}")
    # Broken wikilinks (handle pipe aliases, skip known missing)
    links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content)
    for link in links:
        if link.lower() in KNOWN_MISSING:
            continue
        candidates = [f"{link}.md", f"concepts/{link}.md",
                      f"sources/{link}.md", f"entities/{link}.md",
                      f"synthesis/{link}.md"]
        if not any((WIKI / c).exists() for c in candidates):
            issues.append(f"broken_link:[[{link}]]")
    # Missing phase frontmatter
    if is_concept and not phase:
        issues.append("missing_phase_frontmatter")
    return issues

def main():
    all_pages = list(WIKI.rglob("*.md"))
    all_issues = {}
    for path in all_pages:
        issues = validate_page(path)
        if issues:
            all_issues[str(path)] = issues
    print(f"\nValidation Report — {len(all_pages)} pages checked\n")
    total = sum(len(v) for v in all_issues.values())
    if not all_issues:
        print("  No issues found.")
    else:
        print(f"  {len(all_issues)} pages with issues, {total} total:\n")
        by_code = {}
        for path, issues in sorted(all_issues.items()):
            for issue in issues:
                code = issue.split(":")[0]
                by_code[code] = by_code.get(code, 0) + 1
        for code, count in sorted(by_code.items(), key=lambda x: -x[1]):
            print(f"  {code}: {count}")
    print(f"\n  Total: {len(all_pages)} pages, {total} issues")
    return 0 if total == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
