#!/usr/bin/env python3
"""Synthesis tool: reads 5QLN wiki, generates new FAQ Q&A pairs and concept connections."""

import json
import re
import os
from pathlib import Path
from collections import defaultdict
import argparse
import random

WIKI_ROOT = Path(__file__).parent.parent / "wiki"
DB_DIR = Path(__file__).parent.parent / "database"

def load_all_content():
    """Load all wiki content into memory."""
    docs = {}
    for md_file in WIKI_ROOT.rglob("*.md"):
        if md_file.name.startswith('.') or md_file.name == 'log.md':
            continue
        content = md_file.read_text(errors='ignore')
        docs[md_file.stem] = {
            "content": content,
            "path": str(md_file.relative_to(WIKI_ROOT)),
            "phase": extract_phase(content),
            "title": extract_title(content) or md_file.stem,
        }
    return docs

def extract_phase(content):
    m = re.search(r'^phase:\s*(\w+)', content, re.MULTILINE)
    return m.group(1) if m else None

def extract_title(content):
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return m.group(1).strip() if m else None

def extract_key_concepts(content):
    """Extract 5QLN-specific symbols and terms."""
    symbols = re.findall(r'(?:^|\s)([A-Z][\w]{1,20})(?:$|\s|[,.\)])', content, re.MULTILINE)
    concepts = re.findall(r'\[\[([^\]]+)\]\]', content)
    equations = re.findall(r'[SGQPVA]=\s*[^\n,;]{3,60}', content)
    return {
        "symbols": list(set(symbols))[:10],
        "wikilinks": list(set(concepts)),
        "equations": equations[:5],
    }

def load_existing_faqs():
    """Load existing FAQ entries to avoid duplication."""
    faq_path = DB_DIR / "faq_essence.json"
    if faq_path.exists():
        return set(e['q'].lower() for e in json.loads(faq_path.read_text()))
    return set()

def build_concept_map(docs):
    """Build a map of which concepts connect to which pages."""
    concept_pages = defaultdict(list)
    for name, doc in docs.items():
        for link in doc.get("content", "").split():
            m = re.match(r'\[\[([^\]|]+)', link)
            if m:
                concept_pages[m.group(1)].append(name)
    return concept_pages

def synthesize_faq_pair(topic, docs, concept_pages, existing_faqs):
    """Synthesize a new FAQ Q&A from wiki content."""
    # Find relevant docs
    relevant = []
    topic_lower = topic.lower()
    for name, doc in docs.items():
        score = 0
        c = doc["content"].lower()
        if topic_lower in c: score += 10
        if topic_lower in name.lower().replace("-", " "): score += 5
        if topic_lower in doc.get("title", "").lower(): score += 3
        if score > 0:
            relevant.append((score, name, doc))
    relevant.sort(key=lambda x: -x[0])
    
    if not relevant:
        return None
    
    # Build Q
    question_templates = [
        "What is the relationship between {topic} and {element} in 5QLN?",
        "How does {topic} function across the five phases of 5QLN?",
        "What does {topic} reveal about {element} in the constitutional grammar?",
        "Why is {topic} essential to understanding {element}?",
    ]
    
    # Sample elements from the relevant docs
    sample = relevant[0][2]
    elements = extract_key_concepts(sample["content"])
    
    # Build answer from synthesized synthesis
    sources = list(set(d[2]["path"] for d in relevant[:3]))
    
    answer_parts = []
    answer_parts.append(f"In the 5QLN constitutional grammar, {topic} operates as follows:")
    
    # Add phase-specific observations
    phases_seen = set()
    for score, name, doc in relevant[:5]:
        if doc["phase"] and doc["phase"] not in phases_seen:
            phases_seen.add(doc["phase"])
            answer_parts.append(f"- **{doc['phase'].upper()} phase**: Derived from {doc.get('title', name)}")
    
    # Add symbol connections
    if elements["symbols"]:
        answer_parts.append(f"\nKey symbols involved: {', '.join(elements['symbols'][:5])}")
    
    # Add equation references
    if elements["equations"]:
        answer_parts.append(f"\nRelevant equations: {', '.join(elements['equations'][:3])}")
    
    answer_parts.append(f"\nSources: {'; '.join(sources)}")
    
    answer = "\n".join(answer_parts)
    question = question_templates[random.randint(0, len(question_templates)-1)].format(
        topic=topic,
        element=elements["symbols"][0] if elements["symbols"] else "the framework"
    )
    
    # Deduplicate
    if question.lower() in existing_faqs:
        return None
    
    return {
        "q": question,
        "a": answer,
        "phase": list(phases_seen)[0] if phases_seen else "meta",
        "alpha": "B'' — Synthesized artifact",
        "tags": ["synthesized", topic.lower().replace(" ", "-")],
        "source": "synthesized-from-wiki"
    }

def generate_topic_list(docs):
    """Extract high-value synthesis topics from the wiki."""
    topics = []
    topic_count = defaultdict(int)
    
    for name, doc in docs.items():
        content = doc["content"]
        # Extract potential topic words
        words = re.findall(r'\b(∞0|H=|A=|K|φ|Ω|∇|α|β|∞|L\d|V∅|S=|G=|Q=|P=|V=)\b', content)
        for w in words:
            topic_count[w] += 1
    
    # Sort by frequency
    sorted_topics = sorted(topic_count.items(), key=lambda x: -x[1])
    return [t for t, _ in sorted_topics[:30]]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="5QLN wiki synthesis tool")
    parser.add_argument('--topic', '-t', help='Synthesize FAQ for specific topic')
    parser.add_argument('--generate', '-g', type=int, help='Generate N new FAQ pairs')
    parser.add_argument('--topics', action='store_true', help='List synthesis topics')
    parser.add_argument('--output', '-o', default='-', help='Output file (default: stdout)')
    args = parser.parse_args()

    docs = load_all_content()
    concept_pages = build_concept_map(docs)
    existing_faqs = load_existing_faqs()
    
    print(f"Loaded {len(docs)} documents, {len(existing_faqs)} existing FAQs")

    if args.topics:
        topics = generate_topic_list(docs)
        print("\nSynthesis-ready topics (by frequency):")
        for t in topics:
            print(f"  - {t}")
    
    elif args.topic:
        faq = synthesize_faq_pair(args.topic, docs, concept_pages, existing_faqs)
        if faq:
            print(json.dumps(faq, indent=2, ensure_ascii=False))
        else:
            print(f"Could not synthesize for topic: {args.topic}")
    
    elif args.generate:
        topics = generate_topic_list(docs)
        new_faqs = []
        for topic in topics[:args.generate * 3]:  # Try more than needed
            faq = synthesize_faq_pair(topic, docs, concept_pages, existing_faqs)
            if faq:
                new_faqs.append(faq)
                existing_faqs.add(faq["q"].lower())
            if len(new_faqs) >= args.generate:
                break
        
        if args.output == '-':
            print(json.dumps(new_faqs, indent=2, ensure_ascii=False))
        else:
            Path(args.output).write_text(json.dumps(new_faqs, indent=2, ensure_ascii=False))
            print(f"Wrote {len(new_faqs)} FAQs to {args.output}")
    
    else:
        topics = generate_topic_list(docs)
        print(f"Loaded {len(docs)} docs, {len(existing_faqs)} existing FAQs")
        print(f"Top topics: {topics[:10]}")
        print("\nUsage: --generate N  |  --topic TOPIC  |  --topics")
