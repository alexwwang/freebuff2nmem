---
name: status
description: "Check the status of Nowledge Mem integration and connected AI tools. Use when diagnosing connectivity issues or checking which tools have memory enabled."
argument-hint: ""
level: 1
---

# Check Status

Check the status of Nowledge Mem integration and connected AI tools. Use when diagnosing connectivity issues or checking which tools have memory enabled.

## Usage

```bash
# Check server health
nmem doctor

# Check plugin status
nmem plugins check

# List connected tools
nmem skills hosts

# Check memory count
nmem memories list --limit 5
```

## Interpreting Results

### nmem doctor
- `[ok]` — Component working correctly
- `[warn]` — Component not registered but server is reachable
- `[error]` — Component has issues

### nmem skills hosts
Shows detected AI tools and their skill connection status:
- `installed` — Tool binary found
- `connected` — Skills are linked to the tool

## Troubleshooting

| Issue | Check | Fix |
|---|---|---|
| MCP not connecting | `curl http://<nmem_api_url>/health` | Ensure nmem server is running |
| Skills not loading | `ls ~/.config/manicode/.agents/skills/` | Verify skill directory structure |
| Sync not working | `knowledge-mem-freebuff-sync --dry-run` | Check chat directory permissions |
| Trust prompt反复 | Check `FREEBUFF_TRUST_AGENTS` env | Set to `1` to skip confirmation |
