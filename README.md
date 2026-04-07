# 5QLN Wiki

An LLM-maintained knowledge base for the 5QLN constitutional grammar framework.

Based on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (April 2026).

## The Pattern

Instead of RAG (re-deriving knowledge on every query), the LLM **incrementally builds and maintains a persistent wiki** — a structured, interlinked collection of markdown files. The wiki compounds over time: every source ingested and every question asked makes it richer.

```
You curate sources → LLM compiles the wiki → You read & explore → LLM maintains it all
```

## Architecture

```
5qln-wiki/
├── CLAUDE.md              # Schema — tells the LLM how to operate
├── raw/                   # Immutable source documents (LLM reads, never writes)
│   ├── documents/         # Core 5QLN texts, protocols, specs
│   ├── talks/             # Transcripts, lectures
│   ├── artifacts/         # Code, React components, MCP specs
│   └── images/            # Diagrams, calligraphy
├── wiki/                  # LLM-generated pages (LLM owns this)
│   ├── index.md           # Master catalog
│   ├── log.md             # Chronological operation log
│   ├── overview.md        # Living synthesis
│   ├── concepts/          # Concept pages (S-state, sacred-asymmetry, etc.)
│   ├── entities/          # People, organizations, products
│   ├── sources/           # One summary page per raw source
│   └── outputs/           # Filed query answers, analyses
└── tools/
    └── search.py          # Simple BM25 search over the wiki
```

## Quick Start

### With Claude Code

```bash
cd 5qln-wiki
# Claude Code reads CLAUDE.md automatically

# Drop a source document into raw/documents/
cp ~/my-5qln-doc.md raw/documents/

# Tell Claude Code:
# "Ingest raw/documents/my-5qln-doc.md into the wiki"
```

### With Any LLM Agent

1. Copy the contents of `CLAUDE.md` into your agent's context
2. Point the agent at the `raw/` and `wiki/` directories
3. Tell it to ingest a source

### Search

```bash
python tools/search.py "sacred asymmetry"
python tools/search.py --stats
python tools/search.py --lint
python tools/search.py --index
python tools/search.py --log
```

## Operations

| Command | What It Does |
|---------|-------------|
| **Ingest** | Add a new source → LLM reads it, creates/updates wiki pages |
| **Query** | Ask a question → LLM searches index, synthesizes answer |
| **Lint** | Health check → find contradictions, orphans, gaps |
| **Compile** | Generate outputs → slide decks, glossaries, FAQs |

## View in Obsidian

The wiki is a folder of markdown files. Open it in [Obsidian](https://obsidian.md/) for:
- Graph view (see connections between pages)
- Backlink navigation
- Marp slide rendering (with plugin)
- Dataview queries over frontmatter

## License

MIT — Use freely. The pattern belongs to everyone.

## Credits

- **Pattern:** [Andrej Karpathy — LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (April 2026)
- **Domain:** [5QLN](https://5qln.com) by Amihai Loven
- **Spirit:** Vannevar Bush's Memex (1945) — a personal knowledge store with associative trails
