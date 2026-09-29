---
name: distill-memory
description: "Extract and save durable memories from completed work sessions. Use when a conversation produces valuable decisions, bug fixes, or workflow improvements."
argument-hint: "<what was learned>"
level: 1
---

# Distill Memory

Extract durable memories from completed work and save them to Nowledge Mem. Use when a conversation produces valuable insights worth preserving.

## When to Use

- After completing a substantial task or feature
- When a bug root cause was identified and fixed
- When a workflow improvement was discovered
- When architectural decisions were made
- When the user explicitly asks to "save this" or "remember this"

## What to Save

Focus on **durable facts** that will be useful in future sessions:
- Bug root causes and solutions
- Architecture decisions and constraints
- Workflow preferences and conventions
- Project-specific configurations
- Lessons learned from failures

## What NOT to Save

Avoid saving:
- Process descriptions ("I looked at X, then did Y...")
- Simple confirmations ("Got it", "Okay")
- Transient context already in the current conversation
- Duplicates of existing memories

## Usage

```bash
# Save a decision
nmem --json m add "Content here..." \
  -t "Title of decision" \
  --unit-type decision \
  -i 0.8 \
  -l project-name \
  -l category

# Save a bug fix with root cause
nmem --json m add "Root cause: X. Fix: Y." \
  -t "Bug: add_battery buffer initialization" \
  --unit-type fact \
  -i 0.9 \
  -l meta-pass \
  -l bug

# Save a workflow preference
nmem --json m add "User prefers doc-first approach..." \
  -t "Workflow: doc-first development" \
  --unit-type preference \
  -i 0.7 \
  -l workflow
```

## Unit Types

- `fact` — verified information
- `decision` — choice made with reasoning
- `preference` — user's stated or demonstrated preference
- `plan` — planned approach or roadmap item
- `procedure` — step-by-step instructions
- `learning` — insight gained from experience
- `context` — project or situation background
- `event` — notable occurrence

## Importance Levels

- `0.9` — Critical: bug root causes, security constraints, architecture decisions
- `0.8` — High: workflow rules, known issues, important configurations
- `0.7` — Medium: project conventions, preferences
- `0.6` — Low: general information, background context

## Tips

- Search first to avoid duplicates: `nmem m search "<topic>"`
- One strong memory is better than three weak ones
- Include source provenance: `source_app=freebuff`
- Use labels for easier retrieval: `-l meta-pass -l bug`
