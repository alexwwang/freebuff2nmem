---
name: sync-manicode
description: Extract durable memories from manicode chat history and write to Nowledge Mem. Use when syncing past AI-assisted sessions for reuse.
argument-hint: "<project_name_or_path>"
level: 1
---

# Sync Manicode Chats to Nowledge Mem

将 manicode（codebuff/freebuff）对话历史同步到 Nowledge Mem。

## 数据布局

`~/.config/manicode/projects/<project>/chats/<UTC-timestamp>/`

| 文件 | 用途 |
|---|---|
| `chat-messages.json` | 消息数组（单行 JSON，可达数百 MB） |
| `chat-meta.json` | `{messageCount, firstPrompt, messagesSize}` |
| `run-state.json` | 会话终态：`lastMessage` 或 `error` |
| `log.jsonl` | 运行日志（通常为噪音，跳过） |

## 过滤规则

**只处理含 `chat-messages.json` 的目录**。仅 log.jsonl 的小目录（≤1KB runtime 日志）跳过。

## 提取方法

```python
import json

def extract_text_from_blocks(blocks):
    """从 blocks 中提取 AI 回复文本（content 字段可能为空！）"""
    parts = []
    for b in blocks:
        if b.get('type') == 'text':
            c = b.get('content', '')
            parts.append(c if isinstance(c, str) else
                       '\n'.join(x.get('text','') for x in c if isinstance(x, dict)))
    return '\n'.join(parts).strip()

data = json.load(open('chat-messages.json'))
ai_msgs = [m for m in data if m.get('variant') == 'ai' and m.get('blocks')]
ai_texts = [extract_text_from_blocks(m['blocks']) for m in ai_msgs if extract_text_from_blocks(m['blocks'])]
```

**关键坑**：AI 回复在 `blocks[].content` 里，顶层 `content` 常为空。

## 写入标准

提取 durable facts（而非对话本身）：

1. 用户指令中的**硬性约束**（如"禁止 co-authored commit"、"编译 timeout"）
2. AI 结论中的**事实**：bug 根因、修复方案、文件路径、提交 hash、文档规范
3. `run-state.json` 终态：
   - `lastMessage` → 最终交付物清单
   - `error` → 标记有未完成进度（重要：避免后续会话重做或误判）

## 写入命令

```bash
nmem memories add --stdin \
  --title "记忆标题" \
  --importance 0.7 \
  --label "project,category" \
  --source-app manicode

# 例如
echo "meta-pass bug: add_battery() 未初始化 buffer → garbage display" \
  | nmem memories add --stdin --title "add_battery buffer init bug" --importance 0.8 --label "meta-pass,bug" --source-app manicode
```

## 验证

```bash
# 检查写入是否成功
nmem memories search "<关键词>" --limit 5

# 查看今日新增
nmem memories list --limit 20 | grep "cli.*$(date +%Y-%m-%d)"
```

## 去重

写入前先搜索已有 memory：
```bash
nmem memories search "<主题>" --limit 10
```
已有同类 memory 时用 `nmem memories add --id <existing_id> --stdin` upsert，而非新建。
