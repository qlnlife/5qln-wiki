#!/usr/bin/env python3
"""
5QLN Wiki — Ingest Script
Drops a source into the wiki and triggers the LLM to process it.

Usage:
  python3 ingest.py <source_path> <category> [--title "Title"]
  
Example:
  python3 ingest.py /home/workspace/Datasets/sparkwell-antientropy/data.md sparkwell
"""

import sys
import os
import shutil
from datetime import datetime

WIKI_ROOT = "/home/workspace/5qln-wiki"

def main():
    if len(sys.argv) < 3:
        print("Usage: ingest.py <source_path> <category> [--title 'Title']")
        sys.exit(1)
    
    source_path = sys.argv[1]
    category = sys.argv[2]
    title = None
    
    for i, arg in enumerate(sys.argv):
        if arg == "--title" and i + 1 < len(sys.argv):
            title = sys.argv[i + 1]
    
    if not os.path.exists(source_path):
        print(f"ERROR: Source file not found: {source_path}")
        sys.exit(1)
    
    valid_categories = ["5qln-com", "sparkwell", "sff", "fcf", "self", "projects"]
    if category not in valid_categories:
        print(f"ERROR: Invalid category. Must be one of: {valid_categories}")
        sys.exit(1)
    
    filename = os.path.basename(source_path)
    dest_dir = f"{WIKI_ROOT}/sources/{category}"
    dest_path = f"{dest_dir}/{filename}"
    
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy2(source_path, dest_path)
    
    if title is None:
        title = os.path.splitext(filename)[0].replace("-", " ").replace("_", " ")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    log_entry = f"""
## [{today}] ingest | {title}

**Source:** {dest_path}
**Category:** {category}
**Ingested:** {today}

### Ingest Protocol
1. Read the source in full
2. Extract key information — who, what, when, where, why
3. Update `index.md` with new page entries
4. Update or create relevant entity/concept/session pages
5. Flag any contradictions with existing wiki pages
6. Append this entry to `log.md`

### Key Takeaways (TO FILL)
-

### Pages Touched (TO FILL)
-

### Contradictions Flagged (TO FILL)
-

### ∞0' (TO FILL)
What question does this source open?
"""
    
    print(f"Source copied to: {dest_path}")
    print(f"Log entry to add to log.md:")
    print(log_entry)
    print(f"\nNEXT: Run the 5qln-wiki ingest skill to process this source.")

if __name__ == "__main__":
    main()
