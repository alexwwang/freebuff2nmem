---
name: save-thread
description: "Create a handoff thread in Nowledge Mem for checkpoint or handoff purposes. Use when the user asks for a checkpoint or summary of current work."
argument-hint: "<checkpoint summary>"
level: 1
---

# Save Thread

Create a focused handoff thread in Nowledge Mem for checkpoint or handoff purposes. Use when the user explicitly asks for a checkpoint, summary, or handoff point.

## When to Use

- User asks for a checkpoint or summary
- Before switching to a different task or project
- When handing off work to another agent or session
- At natural completion points of a substantial task

## When NOT to Use

- Automatically after every message
- For routine progress updates
- When the conversation is still ongoing
- When the user hasn't asked for a checkpoint

## Usage

```bash
# Create a handoff thread
nmem --json t create \
  -t "Session Handoff - <topic>" \
  -c "Goal: ... Decisions: ... Files: ... Risks: ... Next: ..." \
  -s generic-agent
```

## Thread Content Guidelines

A good handoff thread includes:
1. **Goal**: What was being worked on
2. **Decisions**: Key decisions made with reasoning
3. **Files**: Important files touched or created
4. **Risks**: Known risks or open questions
5. **Next**: What should happen next

## Example

```bash
nmem --json t create \
  -t "Session Handoff - OTA firmware integration" \
  -c "Goal: Integrate OTA into meta-pass. Decisions: Use feat/ota branch, 4-file upgrade package. Files: .agents/mcp.json, AGENTS.md. Risks: merge-bin stale full.bin issue. Next: Build and test on device." \
  -s generic-agent
```

## Tips

- Keep threads focused and concise
- Include enough context for another agent to continue
- Link to relevant memories with `source_thread`
