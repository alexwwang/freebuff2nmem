---
name: sync-manicode
description: 从 manicode 对话历史中提取持久记忆并写入 Nowledge Mem。支持增量同步（默认）和全量同步。
argument-hint: "<project_name_or_path> [--full] [--dry-run] [--limit N]"
level: 1
---

# Sync Manicode Chats to Nowledge Mem

## 触发条件

- 用户说："同步 manicode 对话" / "sync manicode" / "把历史记录导入 nmem"
- 用户指定项目："同步 <project_name> 的 manicode 历史"
- 用户说："我刚刚完成了一个 long session，帮我保存关键决策"
- 主动检测到新完成的实质性对话（chat-messages.json > 400KB）

## 执行流程

### Step 1: 确定同步模式

```bash
# 增量同步（默认）- 只处理新增或更新的对话
python3 tools/sync_chats.py --project <project_name>

# 全量同步 - 重新处理所有对话
python3 tools/sync_chats.py --project <project_name> --full

# 预览模式 - 不写入，仅显示将处理的内容
python3 tools/sync_chats.py --project <project_name> --dry-run
```

### Step 2: 检查状态文件

状态文件位于：`~/.config/manicode/projects/<project>/.sync-state.json`

```json
{
  "chats": {
    "2026-09-15T07-11-12.935Z": {
      "hash": "8672725a97f1b098",
      "timestamp": "2026-09-29T14:18:40.948881"
    }
  },
  "last_sync": "2026-09-29T14:20:17.209650"
}
```

### Step 3: 执行同步

增量同步逻辑：
1. 计算每个对话目录的 SHA256 哈希值
2. 与状态文件中记录的哈希对比
3. 只处理哈希变化的对话（新增或已修改）
4. 同步完成后更新状态文件

```bash
# 增量同步示例
$ python3 tools/sync_chats.py --project <project_name> --dry-run
Incremental sync: 0 new/updated chat(s) found
All chats are up to date.

# 首次同步或检测到新对话
$ python3 tools/sync_chats.py --project <project_name> --dry-run
Incremental sync: 2 new/updated chat(s) found
Processing 2026-09-26T13-07-06.002Z...
  Found 6 fact(s)
```

### Step 4: 输出报告

```
## Sync Report
- Project: <project_name>
- Mode: incremental|full
- Scanned: <N> directories
- New/Updated: <M> chat(s)
- Facts extracted: <K>
- New memories: <L>
- Updated memories: <P>
- Skipped duplicates: <S>
- Last sync: <timestamp>
```

## 数据源

| 文件 | 用途 |
|---|---|
| `chat-messages.json` | 消息数组（主要数据源） |
| `run-state.json` | 会话终态（lastMessage/error） |
| `chat-meta.json` | 元数据（messageCount 等） |

## 提取规则

**只提取 durable facts（持久事实）**：
- bug 根因与修复方案
- 架构决策与约束
- 工作流规范与偏好
- 已确认的技术细节

**跳过内容**：
- 过程性对话（"让我先..."、"接下来..."）
- 简单的确认回复（"好的"、"明白了"）
- 纯对话性质的交互

## 常见操作

| 场景 | 命令 |
|---|---|
| 日常增量同步 | `python3 tools/sync_chats.py --project <name>` |
| 首次全量同步 | `python3 tools/sync_chats.py --project <name> --full` |
| 预览内容 | `python3 tools/sync_chats.py --project <name> --dry-run` |
| 重置同步状态 | `rm ~/.config/manicode/projects/<name>/.sync-state.json` |
| 同步特定对话 | `python3 tools/sync_chats.py --project-path <chat_dir>` |

## 示例对话

**用户**: 同步 <project_name> 的 manicode 历史
**Agent**:
```
检测到增量同步：6 个实质对话目录
上次同步：2026-09-29T14:20:17
所有对话已同步，无新增内容。
```

**用户**: 我刚完成了一个 long session，帮我保存
**Agent**:
```
检测到新会话: 2026-09-29T15-30-00.000Z
增量同步中...
提取持久事实...
发现 12 条有价值的 decision/bug/constraint...
写入 Nowledge Mem...
✓ Saved 12 facts, state updated
```

**用户**: 重新同步所有历史
**Agent**:
```
全量同步模式
重新处理 6 个对话目录...
提取并去重...
✓ Sync complete: 20 new, 5 updated, 8 duplicates skipped
```
