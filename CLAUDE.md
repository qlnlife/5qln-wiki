# 5QLN Wiki — Schema for LLM Agents

> Based on Karpathy's LLM Wiki pattern (April 2026).
> Adapted for the 5QLN constitutional grammar system.

## What This Is

This is an LLM-maintained wiki for the 5QLN (Five Qualities Language Navigation) knowledge base. The wiki compiles, cross-references, and synthesizes all 5QLN source materials into a persistent, interlinked collection of markdown files. The LLM does all the writing and maintenance. The human (Amihai) curates sources, directs analysis, and asks the right questions.

**Obsidian is the IDE. The LLM is the programmer. The wiki is the codebase.**

---

## Architecture — Three Layers

### 1. Raw Sources (`raw/`)
Immutable source documents. The LLM reads from these but **never modifies them**.

```
raw/
  documents/     # Core 5QLN texts, ECHO protocols, Kernel/Engine docs
  talks/         # 38 "Observing Beauty" transcripts, FCF book chapters
  artifacts/     # React artifacts, TypeScript code, MCP server specs
  images/        # Diagrams, calligraphy, pentagon visualizations
```

**Rules:**
- Never write to `raw/`. It is the source of truth.
- When ingesting, read from `raw/` and write to `wiki/`.
- If a source contradicts the wiki, flag the contradiction — don't silently resolve it.

### 2. The Wiki (`wiki/`)
LLM-generated markdown files. The LLM owns this layer entirely.

```
wiki/
  index.md           # Master catalog of all pages
  log.md             # Chronological record of operations
  overview.md        # High-level synthesis of the entire knowledge base
  concepts/          # Concept pages (e.g., S-state, Known, sacred-asymmetry)
  entities/          # Entity pages (e.g., people, organizations, products)
  sources/           # Source summary pages (one per raw document)
  outputs/           # Filed query answers, comparisons, analyses
```

### 3. This Schema (`CLAUDE.md`)
You're reading it. This tells the LLM how to operate.

---

## 5QLN Domain Knowledge

The wiki tracks a constitutional grammar framework built around:

- **Core Equation:** `H = ∞0 | A = K`
  - Human (H) can dwell in Not-Knowing (∞0) — the Irreducible Unknown
  - AI (A) operates entirely within the Known (K)
  - This is a "sacred asymmetry" — ontological, not merely practical

- **Five-Phase Cycle:** S → G → Q → P → V
  - **S (START):** S = ∞0 → X — emergence from Not-Knowing
  - **G (GROWTH):** G = α ≡ {α'} — pattern recognition, mapping
  - **Q (QUALITY):** Q = φ ∩ Ω — refinement, intersection of form and totality
  - **P (POWER):** P = δE/δV → ∇ — optimization, gradient descent
  - **V (VALUE):** V = L ∩ G → B'' — integration, value crystallization

- **Key Concepts:** FCF (Free Creative Flow), ECHO protocols, HARP (Health/Air/Relationships/Passion), QLN Currency, Pentagon Fractal Shell, Nunc Protocol

- **Product Funnel:** Initiation (AI-agnostic pasteable docs) → Skills (AI-specific) → Plugins (full deployment)

### Tagging Conventions

Every wiki page should include YAML frontmatter:

```yaml
---
title: Page Title
type: concept | entity | source | output
phase: S | G | Q | P | V | meta    # which phase this relates to
tags: [relevant, tags]
sources: [raw/documents/filename.md]  # trace back to raw sources
created: 2026-04-05
updated: 2026-04-05
confidence: high | medium | low       # epistemic status
---
```

### Naming Conventions

- File names: lowercase, hyphens, no spaces. E.g., `sacred-asymmetry.md`
- Wikilinks: use `[[page-name]]` format (Obsidian-compatible)
- Source references: `[Source: raw/documents/filename.md]`

---

## Operations

### INGEST — Adding a New Source

When told to ingest a source:

1. **Read** the raw source completely
2. **Discuss** key takeaways with Amihai (unless told to batch-ingest)
3. **Create** a source summary page in `wiki/sources/`
4. **Update** `wiki/index.md` with the new page
5. **Update or create** relevant concept pages in `wiki/concepts/`
6. **Update or create** relevant entity pages in `wiki/entities/`
7. **Check** for contradictions with existing wiki content — flag them explicitly
8. **Update** cross-references and backlinks across affected pages
9. **Append** an entry to `wiki/log.md`
10. **Update** `wiki/overview.md` if the synthesis has meaningfully changed

**A single source might touch 10–15 wiki pages. That's expected.**

### QUERY — Answering Questions

When asked a question against the wiki:

1. **Read** `wiki/index.md` to find relevant pages
2. **Read** the relevant wiki pages
3. **Synthesize** an answer with citations to wiki pages and raw sources
4. **If the answer is valuable**, ask if it should be filed as a new page in `wiki/outputs/`
5. **Append** the query to `wiki/log.md`

### LINT — Health Check

When told to lint the wiki:

1. **Contradictions:** pages that disagree with each other or with raw sources
2. **Stale claims:** information superseded by newer sources
3. **Orphan pages:** pages with no inbound links
4. **Missing pages:** concepts mentioned in `[[wikilinks]]` but lacking their own page
5. **Missing cross-references:** pages that should link to each other but don't
6. **Data gaps:** important questions the wiki can't answer yet
7. **Phase coverage:** are all five phases (S/G/Q/P/V) adequately documented?
8. **Source tracing:** are important claims traced back to raw sources?
9. **Confidence drift:** are any "high confidence" claims actually uncertain?

Report findings as a structured list. Propose fixes but don't apply them without confirmation.

### COMPILE — Generate Outputs

The wiki can generate derived outputs:

- **Slide decks** (Marp format) from wiki content
- **Comparison tables** between concepts
- **Timelines** of 5QLN development
- **Glossaries** of 5QLN terminology
- **FAQ pages** for onboarding new readers
- **Product documentation** for the Initiation → Skills → Plugins funnel

Outputs go in `wiki/outputs/` and are tracked in the index.

---

## Special Files

### `wiki/index.md`
Content-oriented catalog. Every page listed with:
- Link
- One-line summary
- Type (concept/entity/source/output)
- Phase tag (S/G/Q/P/V/meta)

Organized by category. Updated on every ingest.

### `wiki/log.md`
Chronological, append-only. Format:

```markdown
## [2026-04-05] ingest | Document Title
- Source: raw/documents/filename.md
- Pages created: [[new-page]]
- Pages updated: [[existing-page]], [[another-page]]
- Contradictions found: none
- Notes: brief description
```

### `wiki/overview.md`
A living synthesis document — the "executive summary" of the entire 5QLN knowledge base. Updated whenever the overall picture meaningfully changes.

---

## Integrity Rules

1. **Source grounding:** Important claims must cite raw sources. If unsupported, mark confidence as "low."
2. **Contradiction transparency:** Never silently resolve contradictions. Flag them with `> ⚠️ CONTRADICTION:` callouts.
3. **Idempotent ingest:** Ingesting the same source twice should not distort the wiki.
4. **Separate facts from inferences:** Use `> 💡 INFERENCE:` callouts for editorial synthesis.
5. **Preserve the Irreducible Unknown:** When documenting S-state or ∞0, never reduce it to a mechanism. The wiki documents what can be Known about Not-Knowing without claiming to capture it.

---

## Getting Started

If starting from scratch:

1. Run: `ls raw/` to see what sources are available
2. Start with the most foundational document
3. Ingest it using the INGEST workflow above
4. Repeat for each source, building up the wiki incrementally
5. After every 5–10 sources, run a LINT pass

The wiki compounds. Every source makes it richer. Every query can add to it. The maintenance is near-zero because the LLM handles all the bookkeeping.
