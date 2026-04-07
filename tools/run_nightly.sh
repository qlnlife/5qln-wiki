#!/bin/bash
# run_nightly.sh — 5qln-wiki build pipeline
# Usage: nohup bash tools/run_nightly.sh >> /tmp/wiki_nightly.log 2>&1 &
set -e
DATE=$(date +%Y-%m-%d_%H%M%S)
LOG="/tmp/wiki_nightly_${DATE}.log"
exec > >(tee -a "$LOG") 2>&1

echo "=== 5QLN Wiki Build === $(date)"
cd /home/workspace/5qln-wiki

echo ""
echo "=== [1/4] Crawling 5qln.com ==="
python3 tools/crawl_fresh.py --depth 3 --max-pages 200

echo ""
echo "=== [2/4] Extracting new raw documents ==="
python3 tools/extract_new_pages.py --limit 50

echo ""
echo "=== [3/4] Building wiki (raw → sources → concepts) ==="
python3 tools/wiki_scraper_agent.py --limit 30

echo ""
echo "=== [4/4] Validating ==="
python3 tools/validate_wiki.py

echo ""
echo "=== DONE === $(date)"
