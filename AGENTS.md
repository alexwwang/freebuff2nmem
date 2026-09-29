# Nowledge Mem for freebuff (manicode/codebuff)

You have access to the user's cross-tool knowledge through the `nmem` CLI and five installed skills: `read-working-memory`, `search-memory`, `distill-memory`, `save-thread`, and `status`.

## Context at Session Start

Load the user's current context at the beginning of every session. Prefer Context Bundle because it includes owner identity, resolved AI Identity, active scope, active rules, and Working Memory:

```bash
nmem --json context --source-app freebuff
```

If Context Bundle is not available in this runtime or the installed `nmem` is older, fall back to the lightweight Working Memory briefing:

```bash
nmem --json wm read
```

If this runtime already knows a project or agent lane, add `--space "<space name>"`. Multi-agent orchestrators can set `NMEM_AGENT_ID="<agent-slug>"` before launching freebuff. Use `NMEM_HOST_AGENT_ID` only for stable host-local aliases, and `NMEM_SPACE` only when the whole run should override the identity's default space.

If Context Bundle already includes Working Memory, do not immediately read Working Memory again. Don't re-read during the same session unless the user asks or the session context changes materially.

## Proactive Search

Search when the task connects to prior work, the user references a past decision, or context from before would improve the answer. Don't search speculatively for every message.

```bash
nmem --json m search "query"
```

If the runtime already has an ambient lane, add `--space "<space name>"` to context, memory search, thread search, and save commands.

Use `--mode deep` when the first pass returns weak results or the query is conceptual.

## Retrieval Routing

Use memory search for distilled knowledge (decisions, procedures, preferences). Use thread search for past conversations:

```bash
nmem --json t search "query" --limit 5
nmem --json t show <thread_id> --limit 8 --offset 0 --content-limit 1200
```

Load threads progressively. Increase `--offset` only when the user needs more.

If a memory result includes `source_thread`, inspect the original conversation with `nmem --json t show <thread_id> --limit 8 --offset 0 --content-limit 1200`.

## Autonomous Save

Save proactively when the conversation produces a durable fact, preference, decision, plan, procedure, learning, event, or important context. Don't wait for the user to ask.

```bash
nmem --json m add "content" -t "Title" --unit-type decision -i 0.8
```

Unit types: `fact`, `preference`, `decision`, `plan`, `procedure`, `learning`, `context`, `event`.

Use `-l` to attach labels for easier retrieval: `nmem --json m add "content" -t "Title" --unit-type decision -i 0.8 -l backend -l auth`.

## Syncing Chat History

freebuff does not have a TypeScript Extension API like Pi, so historical chat sync is done manually via the CLI:

```bash
# Preview sessions to import
knowledge-mem-freebuff-sync --project <project_name> --dry-run

# Import sessions
knowledge-mem-freebuff-sync --project <project_name> --apply

# Sync with filters
knowledge-mem-freebuff-sync --project <project_name> --since 2026-09-01 --apply
```

State is tracked in `~/.config/manicode/projects/<project>/.sync-state.json` using SHA256 hashes to detect new/updated conversations.

## Adding to a Project

To enable Nowledge Mem for a new project:

```bash
# Copy MCP config
mkdir -p .agents && cp mcp/mcp.json.example .agents/mcp.json

# Or run the install script
./install.sh ~/path/to/project
```

freebuff will automatically load `.agents/mcp.json` on session start and inject the nmem MCP tools.

## Key Differences from Pi Plugin

| Feature | Pi Plugin | freebuff Plugin |
|---|---|---|
| Context Injection | ✅ TypeScript Extension | ⚠️ Manual AGENTS.md + MCP |
| Auto-sync on completion | ✅ Extension hook | ❌ Manual CLI (sync-history.mjs) |
| Skills | ✅ 5 skills | ✅ 5 skills |
| Sync script | ✅ Built-in | ✅ Available |
| MCP access | ✅ Via extension | ✅ Via .agents/mcp.json |

## Source App Provenance

Keep provenance as `source_app=freebuff`. Use `NMEM_AGENT_ID` only when this freebuff process is intentionally running as a named Nowledge AI Identity.
