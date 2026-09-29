# freebuff2nmem

[English](#english) | [中文](#中文)

---

## English

### What is freebuff2nmem?

**freebuff2nmem** is a bridge that connects your AI coding sessions with persistent memory. It solves a fundamental problem: every time you start a new conversation with an AI coding assistant, it starts from scratch—forgetting previous decisions, architecture constraints, and lessons learned.

This project creates a bidirectional flow between:
- **manicode/freebuff** (your AI coding sessions)
- **Nowledge Mem** (persistent knowledge graph)

### Why does this matter?

When working on complex projects like embedded firmware (embedded device), AI-assisted development generates invaluable context:
- Bug root causes and fixes
- Architecture decisions and constraints  
- Workflow preferences and patterns
- Project-specific conventions

Without persistence, this knowledge is lost between sessions. freebuff2nmem captures it automatically.

### How it works

```
┌──────────────────┐     sync      ┌──────────────────┐     inject     ┌──────────────────┐
│  manicode        │ ─────────────► │  Nowledge Mem    │ ◄───────────── │  Your AI         │
│  (freebuff)      │   Extract      │  (nmem)          │   MCP tools    │  sessions        │
│                  │   durable      │                  │   memory       │                  │
│  - Chat history  │   facts        │  - Searchable    │   recall       │  - Context-aware │
│  - Session logs  │                │    knowledge     │                │  - Learns from   │
│                  │                │  - Durable       │                │    previous work │
└──────────────────┘                └──────────────────┘                └──────────────────┘
```

**Two capabilities:**

| Capability | What it does | When to use |
|---|---|---|
| **Sync** | Extracts durable facts from chat history into persistent memories | After completing important sessions, batch processing |
| **Inject** | Configures MCP so new sessions can query memories in real-time | New project setup, enabling memory access |

### Quick Start

```bash
# Sync existing chat history
python3 tools/sync_chats.py --project <project_name>

# Enable memory for a new project
./install.sh ~/my-project
```

### Key Features

- **Incremental sync**: Only processes new/updated conversations (uses SHA256 hashing)
- **Smart extraction**: Filters out process chatter, keeps only durable facts
- **Automatic injection**: Creates `.agents/mcp.json` and skill files
- **Bilingual support**: Works with both Chinese and English content

### Installation

```bash
# Clone the project
git clone https://github.com/alexwwang/freebuff2nmem.git
cd freebuff2nmem

# Install dependencies
# - nmem (Nowledge Mem CLI)
# - Python 3.8+
# - manicode/freebuff
```

### Requirements

- **manicode/freebuff**: Latest stable version
- **Nowledge Mem**: ≥ 1.0.0 (running on `<nmem_api_url>`)
- **Python**: ≥ 3.8
- **curl**: For health checks

---

## 中文

### 什么是 freebuff2nmem？

**freebuff2nmem** 是连接 AI 编程会话与持久记忆的桥梁。它解决了一个核心问题：每次开启新的 AI 对话时，助手都会从零开始——遗忘之前的决策、架构约束和 learned lessons。

本项目在以下两者之间建立双向连接：
- **manicode/freebuff**（你的 AI 编程会话）
- **Nowledge Mem**（持久化知识图谱）

### 为什么这很重要？

在处理复杂项目（如嵌入式设备时，AI 辅助开发会产生大量有价值上下文：
- Bug 根因与修复方案
- 架构决策与约束
- 工作流偏好与模式
- 项目特定惯例

如果没有持久化机制，这些知识会在会话间丢失。freebuff2nmem 自动捕获它。

### 工作原理

```
┌──────────────────┐     同步      ┌──────────────────┐     注入      ┌──────────────────┐
│  manicode        │ ─────────────► │  Nowledge Mem    │ ◄───────────── │  你的 AI         │
│  (freebuff)      │   提取         │  (nmem)          │   MCP 工具     │  会话            │
│                  │   持久事实     │                  │   记忆检索     │                  │
│  - 对话历史      │                │  - 可搜索        │                │  - 感知上下文的  │
│  - 会话日志      │                │    知识库        │                │  - 从之前工作学习│
└──────────────────┘                └──────────────────┘                └──────────────────┘
```

**两大能力：**

| 能力 | 作用 | 使用场景 |
|---|---|---|
| **同步** | 从对话历史中提取持久事实写入记忆 | 完成重要会话后、批量处理 |
| **注入** | 配置 MCP 使新会话能实时查询记忆 | 新项目初始化、启用记忆功能 |

### 快速开始

```bash
# 同步现有对话历史
python3 tools/sync_chats.py --project <project_name>

# 为新项目启用记忆功能
./install.sh ~/my-project
```

### 核心特性

- **增量同步**：只处理新增或更新的对话（使用 SHA256 哈希比对）
- **智能提取**：过滤过程性闲聊，只保留持久事实
- **自动注入**：创建 `.agents/mcp.json` 和技能文件
- **双语支持**：兼容中英文内容

### 安装

```bash
# 克隆项目
git clone https://github.com/alexwwang/freebuff2nmem.git
cd freebuff2nmem

# 安装依赖
# - nmem（Nowledge Mem CLI）
# - Python 3.8+
# - manicode/freebuff
```

### 依赖要求

- **manicode/freebuff**：最新稳定版
- **Nowledge Mem**：≥ 1.0.0（运行在 `<nmem_api_url>`）
- **Python**：≥ 3.8
- **curl**：用于健康检查

---

## Repository Structure

```
freebuff2nmem/
├── SKILL.md                 # Main skill entry point
├── README.md               # This file
├── AGENTS.md               # Agent routing guide
├── install.sh              # One-command setup script
├── .gitignore
├── skills/
│   ├── sync-manicode/       # Sync skill (manicode → nmem)
│   │   └── SKILL.md
│   └── nowledge-mem-inject/ # Inject skill (nmem → session)
│       └── SKILL.md
├── tools/
│   └── sync_chats.py        # Python sync tool
├── mcp/
│   └── mcp.json.example     # MCP config template
└── docs/
    └── architecture.md      # Architecture documentation
```

## License

MIT License

## Connect

- **GitHub**: [alexwwang/freebuff2nmem](https://github.com/alexwwang/freebuff2nmem)
- **Issues**: Report bugs or request features
