# 5QLN Wiki — Schema
# The configuration file that makes the LLM a disciplined wiki maintainer.

## Origin Question

> *What does a 5QLN wiki look like after 100 sessions?*

This wiki is the living answer. It is not a record of what happened — it IS what happened.

---

## The Three Layers

### Layer 1: Raw Sources
Immutable curated collection. The LLM reads from them but never modifies them.

**Source categories:**
- `sources/5qln-com/` — Articles, papers from 5qln.com
- `sources/sparkwell/` — SparkWell project data, emails, call notes
- `sources/sff/` — Survival & Flourishing Fund grants, criteria
- `sources/fcf/` — FCF source material (Start From Not Knowing, etc.)
- `sources/self/` — Amihai's journal entries, bio, identity documents
- `sources/projects/` — Specific project artifacts (proposals, skills, evaluations)

### Layer 2: The Wiki
LLM-owned directory of markdown files. The LLM creates pages, updates cross-references, maintains structure.

**Wiki structure:**
- `wiki/entities/` — Person pages (Jeffrey Poche, Amihai Loven, collaborators)
- `wiki/concepts/` — Concept pages (SparkWell criteria, SFF alignment, L3 corruption, etc.)
- `wiki/sessions/` — Session artifacts (named by date + topic)
- `wiki/synthesis/` — Overarching synthesis pages (e.g. "What 5QLN Is", "The SparkWell Fit")

### Layer 3: This Schema (AGENTS.md)
The rules, conventions, and workflows. Updated by the LLM as the wiki evolves.

---

## The Operations

### Ingest
1. New source drops into `sources/<category>/`
2. LLM reads the source in full
3. LLM updates `index.md` with new page entries
4. LLM updates relevant entity/concept/session pages
5. LLM appends entry to `log.md`
6. One source may touch 10-15 wiki pages

**Ingest format for log.md:**
```
## [YYYY-MM-DD] ingest | <Source Name>
- Read: <source path>
- Key takeaways: <3-5 bullet points>
- Pages touched: <list of wiki pages updated>
- Contradictions flagged: <yes/no — if yes, note what>
- ∞0' (return question): <what this source opens>
```

### Query
1. Question asked against the wiki
2. LLM reads `index.md` to find relevant pages
3. LLM reads relevant pages
4. LLM synthesizes answer with citations (page links)
5. If answer is valuable → filed back as new wiki page (with citation)

**Query format:**
```
## [YYYY-MM-DD] query | <One-line question summary>
- Asked by: <human / self>
- Pages consulted: <list>
- Synthesis: <answer>
- Filed as: <new wiki page or none>
- ∞0' (new question opened): <question>
```

### Lint
Periodic health check. Ask: contradictions, stale claims, orphan pages, missing cross-references, data gaps.

**Lint format for log.md:**
```
## [YYYY-MM-DD] lint | <Clean|Rot|Needs-attention>
- Contradictions found: <list or none>
- Stale claims: <list or none>
- Orphan pages: <list or none>
- Missing cross-refs: <list or none>
- Gaps identified: <list or none>
- Actions taken: <list or none>
```

---

## Page Types

### Entity Page
```markdown
# <Entity Name>

**Type:** Person | Organization | Project
**Status:** active | archived
**First touched:** YYYY-MM-DD
**Source count:** N

## Summary
One-paragraph synthesis of everything known.

## Key Facts
- <fact>
- <fact>

## Connections
- [[Page Name]] — <relationship>
- [[Page Name]] — <relationship>

## Source References
- [[sources/...]] — <what was extracted>
- [[sources/...]]

## Log
- [YYYY-MM-DD] <event or update>
```

### Concept Page
```markdown
# <Concept>

**Filed under:** entities | synthesis | process
**Related concepts:** [[linked concepts]]
**First introduced:** YYYY-MM-DD
**Source count:** N

## Definition
What this concept means in 5QLN terms.

## Key Claims
- <claim> [^n]
- <claim> [^n]

## Development
How this concept has evolved across sessions.

## Open Questions
What remains unresolved about this concept.

## References
[^n]: <source>
```

### Session Page
```markdown
# YYYY-MM-DD — <Session Topic>

**Phase:** S | G | Q | P | V | Full-cycle
**Participants:** Amihai, 5qln (Zo)
**Duration:** <approx>

## S — What Was Received
X (the question): <>

## G — What Was Illuminated
α (core essence): <>
Y (pattern name): <>

## Q — What Resonated
φ∩Ω (resonance candidate): <>
Z (resonant key): <>

## P — What Flowed
∇ (gradient): <>
A (flow state): <>

## V — What Crystallized
B (decoded output): <>
B'' (artifact): [[file path]]
∞0' (return question): <>

## Corruption Check
- L1: <present | absent>
- L2: <present | absent>
- L3: <present | absent>
- L4: <present | absent>
- V∅: <present | absent>

## Notes
<Miscellaneous>

## ∞0' — What This Opens
<return question>
```

---

## Index Structure

`index.md` is the catalog. Updated on every ingest.

```
# 5QLN Wiki Index

## Entities
| Page | Summary | First Touched | Source Count |
|------|---------|---------------|--------------|
| [[Jeffrey Poche]] | Founder of SparkWell, funder of human-side AI safety | 2026-04-03 | 4 |
| [[Amihai Loven]] | Creator of 5QLN, founder of Epistemic Garden | 2026-03-26 | 12 |

## Concepts
| Page | Summary | Filed Under |
|------|---------|-------------|
| [[L3 Corruption]] | Claiming access to ∞0 — the critical corruption code | synthesis |
| [[SparkWell Fit]] | How 5QLN aligns with SparkWell's criteria | synthesis |

## Sessions
| Page | Topic | Phase | Date |
|------|-------|-------|------|
| [[2026-04-03 — SparkWell Prep]] | Jeffrey Poche call preparation | Full-cycle | 2026-04-03 |
| [[2026-04-07 — LLM Wiki Setup]] | Building the 5QLN wiki from Karpathy pattern | S | 2026-04-07 |

## Synthesis Pages
| Page | Summary |
|------|---------|
| [[What 5QLN Is]] | Comprehensive synthesis across all sources |
| [[The SparkWell Alignment]] | 5QLN fit to SparkWell criteria, updated 2026-04-07 |

## Source Counts
- 5qln-com: 22 articles absorbed
- sparkwell: 4 sources (email, call notes, dataset, evaluation)
- sff: 2 grants reviewed, cross-analysis complete
- fcf: 1 core source (FCF_book.txt)
- self: 14 journal entries, AGENTS.md, SOUL.md, evolution.md
- projects: 6 active project directories

*Last updated: 2026-04-07*
```

---

## Log Structure

`log.md` is append-only. Format each entry as:

```
## [YYYY-MM-DD] <type> | <Title>
<content>
```

Types: `ingest`, `query`, `lint`, `session`, `shift`

Start every entry with `## [YYYY-MM-DD]` for easy grep:
```bash
grep "^## \[" log.md | tail -10
```

---

## Contradiction Detection

When ingesting a new source that contradicts existing wiki claims:
1. Flag the contradiction in the ingest log entry
2. Write the dispute to `sources/contradictions/<source>-vs-<page>.md`
3. Do NOT delete or overwrite — both claims stay visible
4. Resolution: let the contradiction compound until it generates the sharp question

---

## The Holographic Law in the Wiki

Every entity page should reflect all 25 lenses eventually. Every session page should be readable through any phase lens.

The wiki IS the holographic demonstration of 5QLN — every page contains the whole grammar.

---

## Schema Evolution

This schema is a living document. Update it when:
- New source categories are added
- Page types need new fields
- Conventions change based on what works
- Cross-reference patterns emerge

Version: 1.0 — Created 2026-04-07

---

∞0' — What rule does this wiki need that isn't here yet?