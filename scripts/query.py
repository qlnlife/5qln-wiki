#!/usr/bin/env python3
"""
5QLN Wiki — Query Script
Asks a question against the wiki and files the answer back as a page.

Usage:
  python3 query.py "<question>" [--file-as "Page Name"]
  
Example:
  python3 query.py "How does 5QLN align with SparkWell criteria?" --file-as "SparkWell Alignment"
"""

import sys
import os
from datetime import datetime

WIKI_ROOT = "/home/workspace/5qln-wiki"

def main():
    if len(sys.argv) < 2:
        print("Usage: query.py '<question>' [--file-as 'Page Name']")
        sys.exit(1)
    
    question = sys.argv[1]
    file_as = None
    
    for i, arg in enumerate(sys.argv):
        if arg == "--file-as" and i + 1 < len(sys.argv):
            file_as = sys.argv[i + 1]
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    log_entry = f"""
## [{today}] query | {question[:80]}{'...' if len(question) > 80 else ''}

**Asked by:** human
**Date:** {today}

### Query Protocol
1. Read `index.md` to find relevant pages
2. Read relevant pages
3. Synthesize answer with page citations [[Page Name]]
4. If answer is valuable → file as new wiki page
5. Append this entry to `log.md`

### Pages Consulted (TO FILL)
-

### Synthesis (TO FILL)
-

### Filed As (TO FILL)
{"- " + file_as if file_as else "- (do not file — general answer)"}

### ∞0' (TO FILL)
What new question does this answer open?
"""
    
    print(f"Query logged:")
    print(log_entry)
    print(f"\nNEXT: Read index.md and relevant pages, then synthesize.")

if __name__ == "__main__":
    main()
