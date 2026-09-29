---
name: search-memory
description: "Search Nowledge Mem for relevant past decisions, preferences, and knowledge. Use when the task connects to prior work or the user references a past decision."
argument-hint: "<search query>"
level: 1
---

# Search Memory

Search the user's knowledge graph for relevant past decisions, preferences, and knowledge. Use when the task connects to prior work, the user references a past decision, or context from before would improve the answer.

## When to Use

- Task connects to prior work
- User references a past decision
- Context from before would improve the answer
- Uncertain about project conventions or constraints

## When NOT to Use

- Speculatively for every message
- When the question is self-contained
- When the user explicitly wants a fresh start

## Usage

```bash
# Basic search
nmem --json m search "<query>"

# Deep search for conceptual queries
nmem --json m search "<query>" --mode deep

# With space context
nmem --json m search "<query>" --space "<space name>"
```

## Example Queries

```bash
# Search for project-specific knowledge
nmem --json m search "meta-pass architecture"
nmem --json m search "pass-radar v3 constraints"
nmem --json m search "freebuff2nmem integration"

# Search for bug patterns
nmem --json m search "bug root cause"

# Search for workflow preferences
nmem --json m search "commit hygiene rules"
```

## Tips

- Use specific queries related to the current task
- Combine with thread search for conversation history: `nmem --json t search "<query>"`
- Results may include `source_thread` — inspect original conversations if relevant
- Search first before adding new memories to avoid duplicates
