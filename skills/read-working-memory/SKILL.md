---
name: read-working-memory
description: "Load today's Working Memory briefing at session start. Shows your current focus areas, priorities, and recent knowledge changes across all AI tools."
argument-hint: "<optional space name>"
level: 1
---

# Read Working Memory

Start every session with context. Use Context Bundle when owner identity, AI Identity, active scope, or rules could matter; it includes Working Memory. Use Working Memory alone for the current task focus.

## When to Use

**At session start:**

- Beginning of a new conversation
- Returning to a project after a break
- When context about recent work would help

**During session:**

- User asks "what am I working on?" or "what's my context?"
- User references recent priorities or decisions
- Need to understand what has been happening across tools

**Skip when:**

- Already loaded this session
- User explicitly wants a fresh start
- Working on an isolated, context-independent task

## Usage

```bash
nmem --json context --source-app freebuff
```

If the runtime already knows the current project or agent lane, add `--space "<space name>"`. Multi-agent orchestrators can set `NMEM_AGENT_ID="<agent-slug>"` before launching the child agent. Add `NMEM_SPACE` only when that whole run should override the identity's default space. Use `NMEM_HOST_AGENT_ID` only for advanced external aliases.

For only Working Memory:

```bash
nmem --json wm read
```

Or via the skill directly:

```bash
nmem --json m search "working memory today" --limit 5
```
