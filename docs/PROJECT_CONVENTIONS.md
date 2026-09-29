# 项目约定（Project Conventions）

## 敏感数据清理

### 严禁的操作

**禁止使用 repo 替换方式清理历史 commit：**
- ❌ 删除旧仓库 + 创建新仓库
- ❌ gh repo rename + gh repo create
- ❌ 任何导致仓库 URL 变化的操作

### 正确做法

1. **本地重写历史**
   ```bash
   git filter-repo --replace-text <(echo "sensitive==>placeholder")
   ```

2. **推送（如果被工具阻止）**
   ```bash
   # 手动执行
   git push origin master --force
   ```

3. **或使用 GitHub API**
   ```bash
   gh api repos/{owner}/{repo}/commits/{sha} --method DELETE
   ```

### 原因

- Repo 替换会破坏外部链接
- 需要额外的 delete_repo 权限
- 可能引起其他配置丢失（如 visibility 设置）

---
记录时间：2026-09-29
触发事件：freebuff2nmem 敏感数据清理事件
