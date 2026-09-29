---
name: nowledge-mem-inject
description: 将 Nowledge Mem 知识库接入 manicode/freebuff 会话。在以下场景使用：(1) 新项目初始化 (2) 用户要求启用记忆检索 (3) 检测到 .agents 目录缺失 MCP 配置
argument-hint: "<project_path>"
level: 1
---

# Nowledge Mem Injection for Manicode

将 Nowledge Mem 通过 MCP 协议接入 manicode 会话，使 AI 能实时检索历史记忆。

## 触发条件（满足任一即执行）

- 用户说："接入 Nowledge Mem" / "enable memory" / "inject nmem"
- 用户说："让这个项目的 AI 能记住之前的对话"
- 检测到项目根目录缺少 `.agents/mcp.json`
- 用户要求在新项目中启用记忆功能

## 执行流程（按顺序执行）

### Step 1: 检查项目结构

```bash
# 检查是否已集成
if [ -f "$PROJECT_PATH/.agents/mcp.json" ] && grep -q "nowledge-mem" "$PROJECT_PATH/.agents/mcp.json"; then
    echo "ALREADY_CONFIGURED: Nowledge Mem 已接入"
    # 显示当前配置
    cat "$PROJECT_PATH/.agents/mcp.json"
    exit 0
fi

# 检查 AGENTS.md 是否已有集成段
if [ -f "$PROJECT_PATH/AGENTS.md" ] && grep -q "Nowledge Mem" "$PROJECT_PATH/AGENTS.md"; then
    echo "PARTIALLY_CONFIGURED: AGENTS.md 已更新但 MCP 未配置"
fi
```

### Step 2: 创建 .agents 目录和 MCP 配置

```bash
# 创建目录
mkdir -p "$PROJECT_PATH/.agents/skills/nowledge-mem"

# 创建 MCP 配置
cat > "$PROJECT_PATH/.agents/mcp.json" << 'MCP_EOF'
{
  "mcpServers": {
    "nowledge-mem": {
      "url": "http://<nmem_api_url>/mcp",
      "headers": {
        "APP": "manicode",
        "x-nmem-space-protocol": "exact-v1",
        "X-Nmem-Tool-Set": "external-agent",
        "X-Nowledge-Tool-Schema-Profile": "full"
      }
    }
  }
}
MCP_EOF

echo "✓ Created .agents/mcp.json"
```

### Step 3: 创建 Skill 文件

```bash
cat > "$PROJECT_PATH/.agents/skills/nowledge-mem/SKILL.md" << 'SKILL_EOF'
---
name: nowledge-mem
description: 访问 Nowledge Mem 知识库检索历史决策、架构约束和 project 上下文。在开始实质性任务前、完成工作后、或不确定项目惯例时使用。
argument-hint: "<search_query|action>"
level: 1
---

# Nowledge Mem

当前会话已接入 Nowledge Mem。可通过 MCP 工具访问。

## 何时调用

| 场景 | 调用方式 |
|---|---|
| 开始新任务前 | `memory_search("<任务相关关键词>")` |
| 完成工作后 | `memory_add` 保存经验教训 |
| 不确定惯例 | `memory_search("project convention")` |
| 查看今日焦点 | `mem_fs("/working-memory/today.md")` |

## 常用工具

\`\`\`
# 搜索记忆
memory_search(query="meta-pass bug", limit=5)

# 添加新记忆
memory_add(
  title="xxx bug fix",
  content="根因是...解决方案是...",
  labels=["bug", "meta-pass"],
  importance=0.8
)

# 查看 working memory
mem_fs(path="/working-memory/today.md")

# 列出空间
list_spaces()
\`\`\`

## 示例工作流

1. **开始工作前**：
   ```
   使用 nowledge-mem 搜索 "pass-radar v3 约束"
   ```

2. **遇到 bug 时**：
   ```
   使用 nowledge-mem 搜索 "类似 bug"
   解决后：使用 nowledge-mem 添加 "bug root cause + fix"
   ```

3. **完成阶段任务**：
   ```
   使用 nowledge-mem 添加 "阶段交付物 + 待办事项"
   ```
SKILL_EOF

echo "✓ Created .agents/skills/nowledge-mem/SKILL.md"
```

### Step 4: 更新 AGENTS.md

```bash
# 检查 AGENTS.md 是否存在
if [ ! -f "$PROJECT_PATH/AGENTS.md" ]; then
    # 创建新的 AGENTS.md
    cat > "$PROJECT_PATH/AGENTS.md" << 'AGENTSEOF'
# Project Guidelines for AI Agents

## Nowledge Mem Integration

本项目已接入 Nowledge Mem 知识库：
- MCP 端点：`http://<nmem_api_url>/mcp`
- Skill 位置：`.agents/skills/nowledge-mem/SKILL.md`

### 使用规范
1. **开始实质性任务前**：先搜索相关历史决策和架构约束
2. **完成工作后**：添加新的经验教训和决策
3. **不确定惯例时**：搜索现有模式而非猜测

AGENTSEOF
else
    # 追加集成段（如果不存在）
    if ! grep -q "Nowledge Mem Integration" "$PROJECT_PATH/AGENTS.md"; then
        cat >> "$PROJECT_PATH/AGENTS.md" << 'AGENTSEOF'

## Nowledge Mem Integration

本项目已接入 Nowledge Mem 知识库：
- MCP 端点：`http://<nmem_api_url>/mcp`
- Skill 位置：`.agents/skills/nowledge-mem/SKILL.md`

### 使用规范
1. **开始实质性任务前**：先搜索相关历史决策和架构约束
2. **完成工作后**：添加新的经验教训和决策
3. **不确定惯例时**：搜索现有模式而非猜测

AGENTSEOF
        echo "✓ Updated AGENTS.md"
    fi
fi
```

### Step 5: 验证配置

```bash
# 检查 MCP 端点是否可达
curl -s http://<nmem_api_url>/health
# 应返回: {"status":"ok"}

# 检查 nmem 服务状态
nmem status
```

### Step 6: 输出集成报告

```bash
echo ""
echo "## Integration Complete"
echo "- MCP Config: .agents/mcp.json"
echo "- Skill: .agents/skills/nowledge-mem/SKILL.md"
echo "- AGENTS.md: Updated with integration section"
echo ""
echo "Next steps:"
echo "1. Restart manicode in this project"
echo "2. When prompted, trust the MCP server"
echo "   OR set env: export FREEBUFF_TRUST_AGENTS=1"
echo "3. AI will now have access to Nowledge Mem"
```

## 信任确认说明

首次运行时，freebuff 会询问：

```
[agents] Trust MCP server 'nowledge-mem'? (yes/no)
```

**处理方式**：
- 手动确认：用户输入 `y`
- 自动确认：设置环境变量 `export FREEBUFF_TRUST_AGENTS=1`
- 批量配置：在 `~/.config/manicode/settings.json` 中添加 `"trustAgents": true`

## 故障排查

| 问题 | 诊断命令 | 解决方案 |
|---|---|---|
| MCP 连接失败 | `curl -v http://<nmem_api_url>/mcp` | 检查 nmem 服务是否运行 |
| 工具不可见 | `nmem memories list --limit 1` | 确认 nmem CLI 可用 |
| 信任提示反复出现 | 检查 `~/.config/manicode/settings.json` | 添加 `"trustAgents": true` |
| Skill 未加载 | 检查 `.agents/skills/` 目录结构 | 确认 SKILL.md 格式正确 |

## 输出格式

完成后输出：
```
## Nowledge Mem Integration Report
- Project: <project_path>
- MCP Config: .agents/mcp.json
- Skill: .agents/skills/nowledge-mem/SKILL.md
- AGENTS.md: Created/Updated
- Health Check: OK/FAILED
- Next Step: Restart manicode or set FREEBUFF_TRUST_AGENTS=1
```

## 示例对话

**用户**: 帮我把这个项目和 Nowledge Mem 接上
**Agent**:
```
检查项目结构...
发现缺少 .agents/mcp.json
创建 MCP 配置...
创建 Skill 文件...
更新 AGENTS.md...
验证连接...
✓ Integration complete
请重启 manicode 或在启动前设置 FREEBUFF_TRUST_AGENTS=1
```

**用户**: 接入 Nowledge Mem
**Agent**:
```
检测到项目已配置 Nowledge Mem
显示当前配置...
检查连接状态... ✓ OK
无需重新配置
```
