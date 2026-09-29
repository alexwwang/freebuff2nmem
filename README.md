# nowledge-mem-freebuff

[English](#english) | [中文](#中文)

---

## English

### What is it?

**nowledge-mem-freebuff** is a bridge package that connects your freebuff (manicode/codebuff) sessions with **Nowledge Mem**. It gives your AI coding sessions access to persistent cross-tool memory—so decisions, bug fixes, and architecture constraints survive between conversations.

### Why does this matter?

freebuff doesn't have a TypeScript Extension API like Pi. This package works around that limitation with:
- **5 standard skills** for in-session memory access
- **MCP server injection** via `.agents/mcp.json`
- **CLI sync script** for historical chat import

AI-assisted development generates invaluable context during complex projects:
- Bug root causes and fixes
- Architecture decisions and constraints  
- Workflow preferences and patterns
- Project-specific conventions

Without persistence, this knowledge is lost between sessions. nowledge-mem-freebuff captures it.

### How it works

```
┌──────────────────┐     sync       ┌──────────────────┐     inject     ┌──────────────────┐
│  manicode        │ ─────────────► │  Nowledge Mem    │ ◄───────────── │  freebuff        │
│  (freebuff)      │   Extract      │  (nmem)          │   MCP tools    │  (session)       │
│                  │   durable      │                  │   memory       │                  │
│  - Chat history  │   facts        │  - Searchable    │   recall       │  - Context-aware │
│  - Session logs  │                │    knowledge     │                │  - Learns from   │
└──────────────────┘                └──────────────────┘                └──────────────────┘
         ↑                                   │                              │
         └──────── knowledge-mem-freebuff-sync ┘                              └─ .agents/mcp.json
                        (manual CLI, not auto)
```

### Three capabilities

| Capability | What it does | When to use |
|---|---|---|
| **Skills** | `read-working-memory`, `search-memory`, `distill-memory`, `save-thread`, `status` | In-session — agent loads these automatically via `.agents/skills/` |
| **MCP** | Real-time nmem API access during conversation | New project setup — one `.agents/mcp.json` file |
| **Sync** | Import historical chat sessions into Mem threads | Post-session — run CLI manually when convenient |

### Installation

#### Prerequisites

| Dependency | Version | Check Command |
|---|---|---|
| **nmem** | ≥ 1.0.0 | `nmem --version` |
| **Node.js** | ≥ 18 | `node --version` |
| **manicode/freebuff** | Latest | `freebuff --version` |

#### Option 1: Clone and Install (Recommended)

```bash
git clone https://github.com/alexwwang/freebuff2nmem.git
cd freebuff2nmem

# Install into a specific project
./install.sh ~/path/to/my-project
```

The install script will:
1. Create `.agents/mcp.json` (if not present)
2. Copy 5 skills to `.agents/skills/nowledge-mem/`
3. Append Nowledge Mem section to `AGENTS.md`

#### Option 2: Manual Setup

```bash
# Copy MCP config
mkdir -p ~/.agents && cp mcp/mcp.json.example ~/.agents/mcp.json

# Copy skills
mkdir -p ~/.config/manicode/.agents/skills/nowledge-mem/{read-working-memory,search-memory,distill-memory,save-thread,status}
for skill in read-working-memory search-memory distill-memory save-thread status; do
  cp skills/$skill/SKILL.md ~/.config/manicode/.agents/skills/nowledge-mem/$skill/SKILL.md
done

# Copy AGENTS.md
cp AGENTS.md ./AGENTS.md
```

### Quick Start

```bash
# 1. Enable memory for a project
./install.sh ~/path/to/project

# 2. Restart freebuff in that project
# (when prompted, trust the .agents/mcp.json configuration)

# 3. Sync historical sessions
knowledge-mem-freebuff-sync --project my-project --dry-run   # preview first
knowledge-mem-freebuff-sync --project my-project --apply    # import

# 4. Or sync all projects at once
knowledge-mem-freebuff-sync --apply
```

### Sync Script Usage

```bash
# Preview what would be imported
knowledge-mem-freebuff-sync --project <project_name> --dry-run

# Import all matching sessions
knowledge-mem-freebuff-sync --project <project_name> --apply

# Import with filters
knowledge-mem-freebuff-sync --project <project_name> --since 2026-09-01 --apply
knowledge-mem-freebuff-sync --project <project_name> --limit 10 --apply

# Machine-readable output
knowledge-mem-freebuff-sync --json --project <project_name> --dry-run
```

### Key Features

- **Incremental sync**: Only processes new/updated conversations (uses SHA256 hashing via `.sync-state.json`)
- **Smart extraction**: Filters out process chatter, keeps only durable facts
- **Thread-based storage**: Each imported session becomes a Mem thread (not scattered memories)
- **Deduplicated API calls**: Uses `deduplicate` mode to prevent double-imports
- **Bilingual support**: Works with both Chinese and English content

---

## 中文

### 这是什么？

**nowledge-mem-freebuff** 是连接 **freebuff**（manicode/codebuff）与 **Nowledge Mem** 的桥接包。它让你的 AI 编程会话能够访问跨工具的持久记忆——决策、Bug 修复、架构约束都能在对话间延续。

### 为什么重要？

freebuff 不像 Pi 那样有 TypeScript Extension API。本包通过以下方式弥补这一限制：
- **5 个标准 skill** 用于会话内记忆访问
- **MCP 服务器注入** 通过 `.agents/mcp.json`
- **CLI 同步脚本** 用于历史对话导入

AI 辅助开发在处理复杂项目时会产生大量有价值上下文：
- Bug 根因与修复方案
- 架构决策与约束
- 工作流偏好与模式
- 项目特定惯例

没有持久化机制，这些知识会在会话间丢失。nowledge-mem-freebuff 自动捕获它。

### 工作原理

```
┌──────────────────┐     同步       ┌──────────────────┐     注入       ┌──────────────────┐
│  manicode        │ ─────────────► │  Nowledge Mem    │ ◄───────────── │  freebuff        │
│  (freebuff)      │   提取          │  (nmem)          │   MCP 工具     │  （会话）        │
│                  │   持久事实      │                  │   记忆检索     │                  │
│  - 对话历史      │                │  - 可搜索        │                │  - 感知上下文的  │
│  - 会话日志      │                │    知识库        │                │  - 从之前工作学习│
└──────────────────┘                └──────────────────┘                └──────────────────┘
         ↑                                   │                              │
         └──────── knowledge-mem-freebuff-sync ┘                              └─ .agents/mcp.json
                        （手动 CLI，非自动）
```

### 三大能力

| 能力 | 作用 | 使用场景 |
|---|---|---|
| **Skills** | `read-working-memory`, `search-memory`, `distill-memory`, `save-thread`, `status` | 会话内 — 通过 `.agents/skills/` 自动加载 |
| **MCP** | 对话中实时访问 nmem API | 新项目初始化 — 一个 `.agents/mcp.json` 文件 |
| **Sync** | 将历史对话会话导入 Mem threads | 会话后 — 手动运行 CLI |

### 安装

#### 前置依赖

| 依赖 | 版本要求 | 检查命令 |
|---|---|---|
| **nmem** | ≥ 1.0.0 | `nmem --version` |
| **Node.js** | ≥ 18 | `node --version` |
| **manicode/freebuff** | 最新稳定版 | `freebuff --version` |

#### 方式一：克隆并安装（推荐）

```bash
git clone https://github.com/alexwwang/freebuff2nmem.git
cd freebuff2nmem

# 安装到指定项目
./install.sh ~/path/to/my-project
```

安装脚本会：
1. 创建 `.agents/mcp.json`（如不存在）
2. 复制 5 个 skills 到 `.agents/skills/nowledge-mem/`
3. 向 `AGENTS.md` 追加 Nowledge Mem 章节

#### 方式二：手动配置

```bash
# 复制 MCP 配置
mkdir -p ~/.agents && cp mcp/mcp.json.example ~/.agents/mcp.json

# 复制 skills
mkdir -p ~/.config/manicode/.agents/skills/nowledge-mem/{read-working-memory,search-memory,distill-memory,save-thread,status}
for skill in read-working-memory search-memory distill-memory save-thread status; do
  cp skills/$skill/SKILL.md ~/.config/manicode/.agents/skills/nowledge-mem/$skill/SKILL.md
done

# 复制 AGENTS.md
cp AGENTS.md ./AGENTS.md
```

### 快速开始

```bash
# 1. 为新项目启用记忆
./install.sh ~/path/to/project

# 2. 重启 freebuff（提示信任 .agents/mcp.json 时确认）

# 3. 同步历史会话
knowledge-mem-freebuff-sync --project my-project --dry-run   # 先预览
knowledge-mem-freebuff-sync --project my-project --apply    # 再导入

# 4. 或一次性同步所有项目
knowledge-mem-freebuff-sync --apply
```

### Sync 脚本用法

```bash
# 预览要导入的内容
knowledge-mem-freebuff-sync --project <project_name> --dry-run

# 导入所有匹配会话
knowledge-mem-freebuff-sync --project <project_name> --apply

# 带过滤条件导入
knowledge-mem-freebuff-sync --project <project_name> --since 2026-09-01 --apply
knowledge-mem-freebuff-sync --project <project_name> --limit 10 --apply

# 机器可读输出
knowledge-mem-freebuff-sync --json --project <project_name> --dry-run
```

### 核心特性

- **增量同步**：只处理新增或更新的对话（使用 SHA256 哈希 + `.sync-state.json`）
- **智能提取**：过滤过程性闲聊，只保留持久事实
- **Thread 存储**：每个导入会话成为 Mem thread（而非散乱的记忆）
- **幂等 API 调用**：使用 `deduplicate` 模式防止重复导入
- **双语支持**：兼容中英文内容

---

## Repository Structure

```
nowledge-mem-freebuff/
├── package.json              # Plugin manifest (keywords: freebuff-plugin, manicode-plugin)
├── AGENTS.md                 # Usage guide for agents
├── README.md                 # This file
├── install.sh                # One-command project setup
├── .gitignore
├── scripts/
│   └── sync-history.mjs      # Historical chat sync CLI
├── skills/                   # 5 standard nmem skills
│   ├── read-working-memory/
│   ├── search-memory/
│   ├── distill-memory/
│   ├── save-thread/
│   └── status/
└── mcp/
    └── mcp.json.example      # MCP config template
```

## Comparison with Pi Plugin

| Feature | nknowledge-mem-pi | nknowledge-mem-freebuff |
|---|---|---|
| Extension API | ✅ TypeScript lifecycle hooks | ❌ Not supported by freebuff |
| Auto-sync on completion | ✅ Extension hook triggers | ❌ Manual CLI (`sync-history.mjs`) |
| Skills | ✅ 5 skills | ✅ 5 skills |
| Sync script | ✅ Built-in | ✅ Available |
| MCP access | ✅ Via extension | ✅ Via `.agents/mcp.json` |
| Keyword | `pi-package` | `freebuff-plugin`, `manicode-plugin` |

## License

MIT License

## Connect

- **GitHub**: [alexwwang/freebuff2nmem](https://github.com/alexwwang/freebuff2nmem)
- **Issues**: Report bugs or request features
