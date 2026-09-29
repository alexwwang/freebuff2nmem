# Architecture

## Components

### sync_chats.py
- 扫描 manicode 对话目录
- 提取 durable facts（bug 根因、约束、规范、决策）
- 写入 Nowledge Mem via nmem CLI

### mcp.json
- freebuff 原生支持的 MCP 配置格式
- URL-based HTTP streamable transport
- 无需额外进程（nmem 已在 14242 运行）

### SKILL.md (two variants)
- `sync-manicode/`: 指导如何同步历史对话
- `nowledge-mem-inject/`: 指导如何配置 MCP 注入

## Data Flow

```
manicode 会话历史
    ↓
chat-messages.json (JSON array)
    ↓
extract_durable_facts()
    ↓
nmem memories add
    ↓
Nowledge Mem graph
    ↓
mcp.json → HTTP → /mcp endpoint
    ↓
MCP tools (memory_search, etc.)
    ↓
AI 在会话中调用
```

## Integration Points

### freebuff 加载链
1. `process.cwd()` → `.agents/mcp.json`
2. `~/.claude/skills/` → SKILL.md files
3. `~/.agents/` → user-level skills
4. AGENTS.md from project root

### nmem API Surface
- HTTP: `http://<nmem_api_url>`
- MCP: `/mcp` endpoint (streamable HTTP)
- CLI: `nmem memories add/list/search`
- FS: `nmem fs ls /context`

## Design Decisions

1. **为什么用 MCP 而非直接 CLI**
   - MCP 是 manicode 原生支持的扩展机制
   - 工具调用在会话生命周期内持续可用
   - 无需每次 exec 子进程

2. **为什么保留两个 SKILL**
   - sync-manicode: 一次性操作（历史同步）
   - nowledge-mem-inject: 持续运行（会话注入）
   - 职责分离，便于维护

3. **为什么用 URL 而非 command**
   - nmem 是常驻服务（HTTP server）
   - URL-based 更符合 MCP spec
   - 避免 fork/exec 开销
