---
name: freebuff2nmem
description: Bridge between manicode/freebuff sessions and Nowledge Mem. Two capabilities: (1) sync manicode chat history into durable memories, (2) inject Nowledge Mem context into new sessions via MCP configuration. Use when the user wants to connect their AI coding sessions to persistent memory.
argument-hint: "<sync|inject|status> [options]"
level: 1
---

# freebuff2nmem

连接 manicode（codebuff/freebuff）会话与 Nowledge Mem 知识库的桥梁。

## 核心能力

| 能力 | 触发词 | 说明 |
|---|---|---|
| **Sync** | 同步、sync、导入、历史记录 | 将已完成的人机对话提取为持久记忆 |
| **Inject** | 接入、inject、enable memory | 为新项目配置 MCP 使 AI 能实时检索记忆 |
| **Status** | 状态、status、检查 | 检查集成状态和连接健康度 |

## 快速使用

```bash
# 同步历史对话
freebuff2nmem sync --project <project_name>

# 接入新项目
freebuff2nmem inject --project ~/my-new-project

# 检查状态
freebuff2nmem status
```

## 详细用法

### 1. Sync（同步历史）

将 manicode 对话历史中持久有价值的部分提取并写入 Nowledge Mem。

**适用场景**：
- 完成重要 session 后保存关键决策
- 批量同步多个项目的历史对话
- 重建丢失的记忆

**执行逻辑**：
1. 扫描 `~/.config/manicode/projects/<project>/chats/` 目录
2. 过滤实质对话（chat-messages.json > 400KB）
3. 提取 durable facts（bug 根因、约束、规范、决策）
4. 去重检查避免重复写入
5. 写入 Nowledge Mem 并报告结果

**查看完整 skill**: `skills/sync-manicode/SKILL.md`

### 2. Inject（注入配置）

为项目配置 MCP 连接，使 manicode 会话能实时访问 Nowledge Mem。

**适用场景**：
- 新项目初始化
- 启用记忆检索功能
- 修复断开的 MCP 连接

**执行逻辑**：
1. 检查 `.agents/mcp.json` 是否存在且有效
2. 创建/更新 MCP 配置指向 nmem 端点
3. 创建 Skill 文件说明使用方式
4. 更新或创建 `AGENTS.md` 添加集成说明
5. 验证连接健康度

**查看完整 skill**: `skills/nowledge-mem-inject/SKILL.md`

### 3. Status（检查状态）

检查当前项目的集成状态和 nmem 服务健康度。

**输出内容**：
- MCP 配置是否存在
- Skill 文件是否完整
- AGENTS.md 是否包含集成段
- nmem 服务是否运行
- 最近同步记录

## 架构图解

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  Manicode       │         │  freebuff2nmem  │         │  Nowledge Mem   │
│  (freebuff)     │◄────────►│  Bridge         │────────►│  (nmem)         │
│                 │  MCP     │                 │  sync   │                 │
│  - 会话存储      │  config  │  - 配置管理      │         │  - 记忆存储      │
│  - AI 推理       │─────────►│  - 历史同步      │◄────────│  - 语义搜索      │
│  - 工具调用      │  JSON    │  - Skill 管理    │  CLI    │  - 知识图谱      │
└─────────────────┘         └─────────────────┘         └─────────────────┘
        │                          │                          │
        ▼                          ▼                          ▼
  chats/<ts>/              .agents/                     memories/
  ├── chat-messages.json   ├── mcp.json               ├── crystal_xxx
  ├── chat-meta.json       └── skills/                └── ...
  └── run-state.json           └── sync-manicode/
                                   └── nowledge-mem-inject/
```

## 依赖要求

| 组件 | 版本要求 | 检查命令 |
|---|---|---|
| manicode/freebuff | 最新稳定版 | `manicode --version` |
| nmem | ≥ 1.0.0 | `nmem --version` |
| Python | ≥ 3.8 | `python3 --version` |
| curl | 用于 health check | `curl --version` |

## 项目位置

```
~/freebuff2nmem/
├── SKILL.md                 # 本文件（入口）
├── README.md                # 详细说明
├── AGENTS.md               # Agent 路由指南
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

## 故障排查

| 问题 | 可能原因 | 解决步骤 |
|---|---|---|
| 找不到 manicode 目录 | 路径配置错误 | 检查 `~/.config/manicode/projects/` |
| MCP 连接失败 | nmem 服务未启动 | 运行 `nmem serve` 或检查端口 14242 |
| 信任提示反复出现 | 未设置自动信任 | 设置 `FREEBUFF_TRUST_AGENTS=1` |
| 记忆未写入 | nmem CLI 权限问题 | 检查 `nmem memories add` 是否可手动执行 |
| Skill 未加载 | 目录结构错误 | 确认 `.agents/skills/<name>/SKILL.md` 格式 |

## 相关资源

- Nowledge Mem 文档：`nmem --help`
- manicode 文档：`manicode --help`
- MCP 规范：https://modelcontextprotocol.io
