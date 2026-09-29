# Release Notes - v0.1.0

## What's New

**nowledge-mem-freebuff** 是一个为 freebuff (manicode/codebuff) 设计的记忆集成桥接包。

### 核心功能

1. **5 个标准 Skills**
   - `read-working-memory` - 加载工作记忆简报
   - `search-memory` - 搜索已存储的决策和知识
   - `distill-memory` - 提取对话中的持久事实
   - `save-thread` - 创建手递手 thread
   - `status` - 检查 nmem 集成状态

2. **历史对话同步**
   - CLI 脚本 `knowledge-mem-freebuff-sync`
   - 增量同步（SHA256 哈希检测变更）
   - 自动提取 durable facts 并写入 Mem threads
   - 幂等 API 调用防止重复导入

3. **MCP 配置注入**
   - 一键安装到项目 (`./install.sh`)
   - 自动创建 `.agents/mcp.json`
   - 自动复制 skills 到项目目录

### 安装

```bash
git clone https://github.com/alexwwang/freebuff2nmem.git
cd freebuff2nmem
./install.sh ~/path/to/project
```

### 同步历史

```bash
# 预览要导入的会话
knowledge-mem-freebuff-sync --project <project_name> --dry-run

# 导入
knowledge-mem-freebuff-sync --project <project_name> --apply
```

## Changelog

- v0.1.0 (2026-09-29): Initial release
  - 标准 nmem plugin 包格式
  - 5 个 skills + sync CLI
  - .sync-state.json 状态管理
  - 双语 README

## Known Limitations

- freebuff 不支持 TypeScript Extension API（对比 Pi 插件）
- 历史同步需要手动运行 CLI，无自动 hook
