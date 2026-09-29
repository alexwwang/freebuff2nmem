---
name: nowledge-mem-inject
description: Inject Nowledge Mem context into manicode/freebuff sessions via MCP configuration. Use when setting up a new project or enabling memory recall for existing projects.
argument-hint: "<project_path>"
level: 1
---

# Nowledge Mem Injection for Manicode

将 Nowledge Mem 知识库接入 manicode（codebuff/freebuff）会话，使 AI 能自动检索历史记忆。

## 工作原理

freebuff（manicode 的推理内核）原生支持两种上下文注入机制：

| 机制 | 路径 | 用途 |
|---|---|---|
| MCP 服务器 | `.agents/mcp.json` | 运行时工具调用（memory_search, memory_add 等） |
| AGENTS.md | `<project>/AGENTS.md` | 系统级约定和文档注入 |

## 快速集成

### 步骤 1：创建 .agents/mcp.json

在项目根目录创建 `.agents/mcp.json`：

```json
{
  "mcpServers": {
    "nowledge-mem": {
      "url": "http://<nmem_api_url>/mcp"
    }
  }
}
```

### 步骤 2：更新 AGENTS.md

在 `AGENTS.md` 中添加 Nowledge Mem 集成段：

```markdown
## Nowledge Mem Integration

本会话可通过 MCP 访问 Nowledge Mem：
- 端点：`http://<nmem_api_url>/mcp`
- 工具：memory_search, memory_add, mem_fs, find_skills, ...
- Skill：`.agents/skills/nowledge-mem/SKILL.md`

### 何时使用
- 开始实质性任务前：搜索相关历史决策和架构约束
- 完成工作后：添加新的经验教训
- 不确定惯例时：搜索现有模式
```

### 步骤 3：创建 skill（可选）

```bash
mkdir -p .agents/skills/nowledge-mem
cat > .agents/skills/nowledge-mem/SKILL.md << 'SKILL_EOF'
---
name: nowledge-mem
description: Access Nowledge Mem knowledge graph for memory search and recall.
argument-hint: "<search_query>"
level: 1
---

# Nowledge Mem

当前会话已接入 Nowledge Mem。使用以下方式检索记忆：

## 快速使用
使用 nowledge-mem 搜索 "<关键词>"
查看 working-memory 今日焦点
SKILL_EOF
```

## 信任确认

首次运行时，freebuff 会询问是否信任 `.agents/mcp.json`：

```
[agents] Trust MCP server 'nowledge-mem'? (yes/no)
```

输入 `y` 确认。后续启动免确认。

或使用环境变量：

```bash
export FREEBUFF_TRUST_AGENTS=1
```

## 验证连接

```bash
# MCP 端点健康检查
curl -s http://<nmem_api_url>/health
# 应返回: {"status":"ok"}

# 检查工具可用
nmem memories list --limit 5
```

## 可用工具

通过 nmem MCP 可调用 65+ 工具，核心包括：

| 工具 | 用途 |
|---|---|
| `memory_search` | 语义搜索记忆 |
| `memory_add` | 创建新记忆 |
| `get_memory_by_id` | 按 ID 获取 |
| `mem_fs` | 读取 Nowledge FS |
| `find_skills` | 搜索技能 |
| `list_spaces` | 列出知识空间 |
| `library_add` | 添加到知识库 |

## 项目示例

已完成集成的项目：
- `/Users/alex/<project_name>/` — meta-pass + pass-radar 双项目
- MCP 配置：`.agents/mcp.json`
- Skill：`.agents/skills/nowledge-mem/SKILL.md`
