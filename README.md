# freebuff2nmem

将 manicode（codebuff/freebuff）会话与 Nowledge Mem 知识库打通的集成项目。

## 能力概述

### 1. 同步（Sync）

将 manicode 对话历史提取为 durable memories 写入 Nowledge Mem。

```bash
# 同步指定项目
python3 tools/sync_chats.py --project <project_name>

# 指定路径
python3 tools/sync_chats.py --project-path ~/.config/manicode/projects/myproject

# 预览模式（不写入）
python3 tools/sync_chats.py --dry-run
```

### 2. 注入（Inject）

在新项目中配置 MCP + Skill，让 manicode 会话自动访问 Nowledge Mem。

```bash
# 快速安装
./install.sh ~/my-project
```

## 目录结构

```
freebuff2nmem/
├── SKILL.md                          # 本 skill 入口
├── README.md                         # 项目说明（本文件）
├── AGENTS.md                         # AI agent 路由说明
├── install.sh                        # 快速安装脚本
├── .gitignore
├── skills/
│   ├── sync-manicode/               # 同步 skill
│   └── nowledge-mem-inject/         # 注入 skill
├── tools/
│   └── sync_chats.py                # 同步工具脚本
├── mcp/
│   └── mcp.json.example             # MCP 配置模板
└── docs/
    └── architecture.md              # 架构文档
```

## 工作原理

```
┌─────────────────┐      ┌─────────────────┐
│  Manicode       │      │  Nowledge Mem   │
│  (freebuff)     │      │  (nmem)         │
│                 │      │                 │
│  .agents/       │      │  Memory Graph   │
│  ├── mcp.json  │◄────►│  ├── Search    │
│  └── skills/   │      │  ├── Add       │
│                 │      │  └── Recall    │
└─────────────────┘      └─────────────────┘
```

1. **manicode** 启动时扫描 `.agents/mcp.json`
2. 连接到 `http://<nmem_api_url>/mcp`（nmem MCP 端点）
3. 获得 65+ MCP 工具（memory_search, memory_add, mem_fs 等）
4. AI 在对话中调用这些工具检索/写入记忆

## 快速开始

### 同步已有对话

```bash
# 进入项目目录
cd ~/<project_name>

# 运行同步
python3 ~/freebuff2nmem/tools/sync_chats.py --project <project_name>
```

### 为新项目启用记忆注入

```bash
# 运行安装脚本
~/freebuff2nmem/install.sh ~/<project_name>
```

安装后会创建：
- `.agents/mcp.json` - MCP 配置
- `.agents/skills/nowledge-mem/SKILL.md` - 项目级 skill
- `AGENTS.md` - 根 AGENTS.md（如不存在）

## 验证连接

```bash
# 检查 nmem 健康
curl -s http://<nmem_api_url>/health

# 检查工具可用
nmem memories list --limit 5
```

## 配置自定义端点

如果 nmem 运行在其他端口或主机，修改 `mcp.json`：

```json
{
  "mcpServers": {
    "nowledge-mem": {
      "url": "http://your-host:14242/mcp"
    }
  }
}
```

## 限制与注意事项

- AI 回复文本在 `blocks[].content` 中，不在顶层 `content` 字段
- 仅 log.jsonl 的小目录（≤1KB）跳过，无实质内容
- 大 JSON 文件用 `json.load()` 读取，勿整行 read
- run-state.json 终态（lastMessage/error）需单独提取
- 首次信任 MCP 服务器：输入 `y` 或使用 `FREEBUFF_TRUST_AGENTS=1`
