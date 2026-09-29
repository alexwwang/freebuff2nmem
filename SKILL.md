---
name: freebuff2nmem
description: Bridge between manicode/freebuff (Codebuff) sessions and Nowledge Mem. Two capabilities: (1) sync manicode chat history into durable memories, (2) inject Nowledge Mem context into new sessions via MCP + skill injection.
argument-hint: "<sync|recall|inject> [options]"
level: 1
---

# freebuff2nmem

本项目将 manicode（别名 codebuff）会话历史与 Nowledge Mem 知识库打通，实现双向集成：

1. **同步（sync）**：将 manicode 对话历史提取为 durable memories 写入 Nowledge Mem
2. **注入（inject）**：在新会话中通过 MCP + skill 自动检索 Nowledge Mem 记忆

## 目录结构

```
~/freebuff2nmem/
├── SKILL.md                  # 本 skill 入口
├── README.md                 # 项目说明
├── AGENTS.md                 # AI agent 路由与集成说明
├── .gitignore
├── skills/
│   ├── sync-manicode/        # 同步 skill：manicode → nmem
│   └── nowledge-mem-inject/  # 注入 skill：nmem → 会话上下文
├── tools/
│   └── sync_chats.py         # 同步工具脚本
├── mcp/
│   └── mcp.json.example      # MCP 配置模板
└── docs/
    └── architecture.md       # 架构文档
```

## 使用场景

### 场景 1：同步历史对话
```bash
# 同步 <project_name> 项目的所有 manicode 对话
python3 tools/sync_chats.py --project <project_name> --limit 50

# 指定项目路径
python3 tools/sync_chats.py --project ~/.config/manicode/projects/myproject
```

### 场景 2：新会话自动注入
在目标项目根目录创建 `.agents/mcp.json` 和 `AGENTS.md`：
```json
{
  "mcpServers": {
    "nowledge-mem": {
      "url": "http://<nmem_api_url>/mcp"
    }
  }
}
```

然后在 `AGENTS.md` 中添加：
```markdown
## Nowledge Mem Integration
本会话可通过 MCP 访问 Nowledge Mem。使用前搜索相关记忆。
```

## 工作原理

1. 扫描 `~/.config/manicode/projects/<project>/chats/*/` 目录
2. 过滤出含 `chat-messages.json` 的实质对话
3. 提取 user prompt 和 AI response（从 blocks 中取 text 类型）
4. 按 durable facts 标准筛选（bug 根因、约束、规范、决策）
5. 调用 `nmem memories add --stdin` 写入
6. 同步记录元数据（来源路径、时间戳）

## 已知坑点

- AI 回复在 `blocks[].content` 而非顶层 `content` 字段
- 仅 log.jsonl 的空 stub 目录跳过（无价值）
- 大 JSON 文件用 python `json.load()` 读取，勿整行 read
- run-state.json 终态（lastMessage/error）必须单独提取
