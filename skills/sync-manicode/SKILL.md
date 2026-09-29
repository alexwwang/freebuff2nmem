---
name: sync-manicode
description: 从 manicode 对话历史中提取持久记忆并写入 Nowledge Mem。在以下场景使用：(1) 用户要求同步历史对话 (2) 检测到新完成的 manicode 会话 (3) 主动建议同步有价值的会话
argument-hint: "<project_name_or_path> [--dry-run] [--limit N]"
level: 1
---

# Sync Manicode Chats to Nowledge Mem

## 触发条件（满足任一即执行）

- 用户说："同步 manicode 对话" / "sync manicode" / "把历史记录导入 nmem"
- 用户指定项目："同步 <project_name> 的 manicode 历史"
- 用户说："我刚刚完成了一个 long session，帮我保存关键决策"
- 检测到 `~/.config/manicode/projects/<project>/chats/` 下有新的实质性对话（chat-messages.json > 400KB）

## 执行流程（按顺序执行）

### Step 1: 定位对话目录

```bash
# 如果用户指定了项目名
PROJECT_PATH="$HOME/.config/manicode/projects/$1/chats"

# 如果用户指定了路径
PROJECT_PATH="$1/chats"

# 列出所有对话目录
ls -lh "$PROJECT_PATH"
```

### Step 2: 过滤实质对话

只处理包含 `chat-messages.json` 且大小 > 400KB 的目录：

```bash
for dir in "$PROJECT_PATH"/*/; do
    msgs="$dir/chat-messages.json"
    if [ -f "$msgs" ] && [ $(stat -f%z "$msgs" 2>/dev/null || stat -c%s "$msgs") -gt 400000 ]; then
        echo "$(basename $dir) $(stat -f%z "$msgs" 2>/dev/null || stat -c%s "$msgs") bytes"
    fi
done
```

跳过仅含 log.jsonl 的小目录（≤1KB runtime 日志）。

### Step 3: 提取 durable facts

使用 Python 脚本提取持久事实：

```bash
python3 << 'PYEOF'
import json, re, sys
from pathlib import Path

def extract_text(blocks):
    """从 blocks 提取 AI 回复文本（content 字段可能为空！）"""
    parts = []
    for b in blocks:
        if b.get('type') == 'text':
            c = b.get('content', '')
            parts.append(c if isinstance(c, str) else
                       '\n'.join(x.get('text','') for x in c if isinstance(x, dict)))
    return '\n'.join(parts).strip()

def is_durable_fact(text):
    """判断是否为持久事实（而非对话过程）"""
    # 排除的过程性内容
    process_patterns = [
        r'让我先', r'接下来', r'我会', r'现在我需要',
        r'首先', r'然后', r'最后', r'好的，我来'
    ]
    if any(re.search(p, text[:100]) for p in process_patterns):
        return False
    
    # 必须包含的事实性信号
    fact_signals = [
        r'\d{6,}-signed\.bin', r'commit [a-f0-9]{7,}', r'0x[0-9a-fA-F]{4,}',
        r'BUG[SD]-?\d*', r'已修复|已确认|根因|解决方案|约束|规范',
        r'partitions\.csv|slot.*size|nvs.*offset',
        r'meta-pass|pass-radar|freebuff|manicode'
    ]
    return any(re.search(p, text) for p in fact_signals)

chats_dir = Path('$PROJECT_PATH')
facts = []

for chat_dir in sorted(chats_dir.iterdir()):
    msgs_file = chat_dir / 'chat-messages.json'
    if not msgs_file.exists():
        continue
    
    with open(msgs_file) as f:
        data = json.load(f)
    
    # 提取 AI 回复
    ai_msgs = [m for m in data if m.get('variant') == 'ai' and m.get('blocks')]
    ai_texts = [extract_text(m['blocks']) for m in ai_msgs 
                if extract_text(m['blocks']) and is_durable_fact(extract_text(m['blocks']))]
    
    ts = chat_dir.name
    for i, txt in enumerate(ai_texts[:5]):
        # 提取标题（第一行有意义的部分）
        lines = [l.strip() for l in txt.split('\n') if l.strip() and len(l.strip()) > 10]
        title = lines[0][:80] if lines else f'Fact from {ts}'
        
        facts.append({
            'timestamp': ts,
            'title': title,
            'content': txt[:1000],
            'source': str(chat_dir)
        })

# 输出 facts（用于后续写入）
import json as j
print(j.dumps(facts, ensure_ascii=False, indent=2))
PYEOF
```

### Step 4: 去重检查

对每个 fact 搜索已有记忆：

```bash
nmem memories search "<关键词>" --limit 5
```

如果找到高度相似的已有记忆，记录其 ID 用于 upsert。

### Step 5: 写入 Nowledge Mem

```bash
# 单个 fact 写入模板
echo "<fact_content>" | nmem memories add \
  --title "<fact_title>" \
  --importance 0.7 \
  --label "manicode-sync,<project>,<category>" \
  --source-app freebuff2nmem

# 如果有重复，使用 upsert
echo "<fact_content>" | nmem memories add \
  --id "<existing_id>" \
  --title "<updated_title>" \
  --importance 0.7 \
  --label "manicode-sync,<project>,<category>" \
  --source-app freebuff2nmem
```

**Importance 分级规则**：
- 0.9: bug 根因、架构决策、安全约束
- 0.8: 工作流程、技术规范、已知陷阱
- 0.7: 项目惯例、偏好设置
- 0.6: 一般性信息、背景知识

### Step 6: 验证写入

```bash
# 检查今日写入
nmem memories list --limit 20 | grep "cli.*$(date +%Y-%m-%d)"

# 抽样验证
nmem memories search "<关键词>" --limit 3
```

### Step 7: 输出报告

向用户报告：
```
✓ 扫描 <N> 个对话目录，识别 <M> 个实质对话
✓ 提取 <K> 条持久事实
✓ 写入 <L> 条新记忆，<P> 条更新
✓ 跳过 <S> 条重复记忆
```

## 输出格式

完成后输出：
```
## Sync Report
- Project: <project_name>
- Scanned: <N> directories
- Facts extracted: <K>
- New memories: <L>
- Updated memories: <P>
- Skipped duplicates: <S>
- Source: ~/.config/manicode/projects/<project>/chats/
```

## 错误处理

| 错误 | 处理 |
|---|---|
| 项目路径不存在 | 提示用户提供正确路径 |
| nmem 服务不可用 | 提示运行 `nmem serve` 或检查配置 |
| JSON 解析失败 | 跳过损坏文件，记录警告 |
| 无实质对话 | 告知用户无需要同步的内容 |

## 示例对话

**用户**: 同步 <project_name> 的 manicode 历史
**Agent**: 
```
扫描到 6 个实质对话目录...
提取 durable facts...
找到 31 条潜在事实，去重后写入 20 条新记忆...
✓ Sync complete: 20 new, 3 updated, 8 duplicates skipped
```

**用户**: 我刚完成了一个 long session，帮我保存
**Agent**:
```
检测到最近会话: 2026-09-29T10-30-00.000Z
提取持久事实...
发现 12 条有价值的 decision/bug/constraint...
写入 Nowledge Mem...
✓ Saved 12 facts
```
