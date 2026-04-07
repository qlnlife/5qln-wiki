#!/bin/bash
# run_nightly.sh — Overnight automation for 5qln-wiki build.
# Usage: nohup bash run_nightly.sh >> /tmp/wiki_nightly.log 2>&1 &
# Or cron: 0 2 * * * /home/workspace/5qln-wiki/tools/run_nightly.sh
set -e
DATE=$(date +%Y-%m-%d_%H%M%S)
LOG="/tmp/wiki_nightly_${DATE}.log"
exec > >(tee -a "$LOG") 2>&1
echo "=== 5QLN Wiki Nightly Build === $(date)"
TOOLS=$(dirname "$0")
cd "$TOOLS/.."
echo ""
echo "=== [1/4] Crawling 5qln.com ==="
python3 tools/crawl_fresh.py --depth 3 --max-pages 200
echo ""
echo "=== [2/4] Extracting new raw documents ==="
python3 tools/extract_new_pages.py --limit 50
echo ""
echo "=== [3/4] Running wiki_scraper_agent ==="
python3 tools/wiki_scraper_agent.py --limit 30
echo ""
echo "=== [4/4] Validating wiki ==="
python3 tools/validate_wiki.py
echo ""
echo "=== DONE === $(date)"
