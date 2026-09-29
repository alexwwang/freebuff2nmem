# freebuff2nmem

将 manicode（codebuff/freebuff）会话与 Nowledge Mem 知识库打通的桥梁项目。

## 快速开始

### 方式一：让 AI 帮你配置（推荐）

在 manicode 中加载本 SKILL，然后直接告诉 AI 你的需求：

```
你：帮我同步 <project_name> 的 manicode 历史
你：把这个项目和 Nowledge Mem 接上
你：检查我的记忆集成状态
```

AI 会自动执行对应的 sync/inject/status 操作。

### 方式二：命令行直接使用

```bash
# 同步指定项目的对话历史
python3 tools/sync_chats.py --project <project_name> --dry-run

# 为新项目启用记忆注入
./install.sh ~/my-project

# 检查 nmem 服务状态
curl http://<nmem_api_url>/health
```

## 两个核心能力

### 1. Sync（同步历史）

将已完成的人机对话提取为持久记忆。

**做什么**：
- 扫描 `~/.config/manicode/projects/<project>/chats/`
- 过滤实质对话（chat-messages.json > 400KB）
- 提取 durable facts（bug 根因、约束、规范、决策）
- 写入 Nowledge Mem 并去重

**何时用**：
- 完成重要 session 后
- 批量整理历史对话
- 重建丢失的记忆

**查看 skill**: `skills/sync-manicode/SKILL.md`

### 2. Inject（注入配置）

为项目配置 MCP 连接，使 AI 能实时检索记忆。

**做什么**：
- 创建 `.agents/mcp.json` 指向 nmem 端点
- 创建 Skill 文件说明使用方式
- 更新 `AGENTS.md` 添加集成说明
- 验证连接健康度

**何时用**：
- 新项目初始化
- 启用记忆检索功能
- 修复断开的 MCP 连接

**查看 skill**: `skills/nowledge-mem-inject/SKILL.md`

## 工作原理

```
manicode 会话历史
       │
       ▼
  sync_chats.py 提取 durable facts
       │
       ▼
  Nowledge Mem (nmem)
       │
       ▼  MCP HTTP
  新会话中的 AI 自动检索记忆
```

**关键点**：
- AI 回复文本在 `blocks[].content`，不在顶层 `content`
- 只同步 durable facts，不复制对话过程
- MCP 配置让 AI 在会话中随时调用 `memory_search` 等工具

## 项目结构

```
freebuff2nmem/
├── SKILL.md                 # Agent 入口（加载此文件）
├── README.md               # 本文档
├── AGENTS.md               # AI agent 路由指南
├── install.sh              # 一键安装脚本
├── .gitignore
├── skills/
│   ├── sync-manicode/       # 同步 skill
│   │   └── SKILL.md
│   └── nowledge-mem-inject/ # 注入 skill
│       └── SKILL.md
├── tools/
│   └── sync_chats.py        # Python 同步工具
├── mcp/
│   └── mcp.json.example     # MCP 配置模板
└── docs/
    └── architecture.md      # 架构文档
```

## 依赖

- manicode/freebuff（最新版本）
- nmem（≥ 1.0.0，运行在 <nmem_api_url>）
- Python 3.8+
- curl（用于 health check）

## 故障排查

| 问题 | 检查项 |
|---|---|
| MCP 连接失败 | `curl http://<nmem_api_url>/health` |
| 找不到对话 | 检查 `~/.config/manicode/projects/` 目录 |
| 信任提示反复 | 设置 `FREEBUFF_TRUST_AGENTS=1` |
| Skill 未加载 | 确认 `.agents/skills/<name>/SKILL.md` 存在 |

## 示例对话

**用户**: 同步 <project_name> 的 manicode 历史
**Agent**: 执行 sync-manicode skill，扫描 6 个对话，提取 20 条 facts，写入 nmem

**用户**: 帮我把这个项目和记忆系统接上
**Agent**: 执行 nowledge-mem-inject skill，创建 .agents/ 配置，输出集成报告

**用户**: 检查我的记忆集成状态
**Agent**: 执行 status 检查，输出 MCP 配置、Skill 加载、连接健康度

## 学习更多

- 架构设计：`docs/architecture.md`
- Agent 路由：`AGENTS.md`
- 各 skill 详细用法：`skills/*/SKILL.md`
