#!/bin/bash
# install.sh - Install freebuff2nmem integration into a project

set -e

PROJECT_PATH="${1:-.}"

if [ ! -d "$PROJECT_PATH" ]; then
    echo "ERROR: Project path not found: $PROJECT_PATH"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$PROJECT_PATH" && pwd)"

echo "Installing freebuff2nmem into: $PROJECT_DIR"

# 1. Create .agents directory
mkdir -p "$PROJECT_DIR/.agents/skills/nowledge-mem"

# 2. Copy MCP config
if [ ! -f "$PROJECT_DIR/.agents/mcp.json" ]; then
    cp "$SCRIPT_DIR/mcp/mcp.json.example" "$PROJECT_DIR/.agents/mcp.json"
    echo "✓ Created .agents/mcp.json"
else
    echo "⊘ Skipping .agents/mcp.json (already exists)"
fi

# 3. Copy skill
cp "$SCRIPT_DIR/skills/nowledge-mem-inject/SKILL.md" "$PROJECT_DIR/.agents/skills/nowledge-mem/SKILL.md"
echo "✓ Created .agents/skills/nowledge-mem/SKILL.md"

# 4. Create or update AGENTS.md
if [ ! -f "$PROJECT_DIR/AGENTS.md" ]; then
    cat > "$PROJECT_DIR/AGENTS.md" << 'EOF'
# Project Guidelines for AI Agents

## Nowledge Mem Integration

This project has automatic access to Nowledge Mem via MCP:
- MCP config: `.agents/mcp.json`
- Endpoint: `http://<nmem_api_url>/mcp`
- Skill: `.agents/skills/nowledge-mem/SKILL.md`

### When to use Nowledge Mem
- Before starting work on firmware, UI, or protocols: recall architecture doctrine and known bugs
- After completing substantial work: add learnings and workflow improvements
- When making architectural decisions: check existing constraints

### Quick patterns
\`\`\`
# Recall project knowledge
使用 nowledge-mem 搜索 "项目相关主题"

# Check working memory
查看 working-memory 今日焦点
\`\`\`

---

EOF
    echo "✓ Created AGENTS.md"
else
    # Append section if not present
    if ! grep -q "Nowledge Mem Integration" "$PROJECT_DIR/AGENTS.md"; then
        cat >> "$PROJECT_DIR/AGENTS.md" << 'EOF'

## Nowledge Mem Integration

This project has automatic access to Nowledge Mem via MCP:
- MCP config: `.agents/mcp.json`
- Endpoint: `http://<nmem_api_url>/mcp`
- Skill: `.agents/skills/nowledge-mem/SKILL.md`

### When to use Nowledge Mem
- Before starting work on firmware, UI, or protocols: recall architecture doctrine and known bugs
- After completing substantial work: add learnings and workflow improvements
- When making architectural decisions: check existing constraints

### Quick patterns
\`\`\`
# Recall project knowledge
使用 nowledge-mem 搜索 "项目相关主题"

# Check working memory
查看 working-memory 今日焦点
\`\`\`

EOF
        echo "✓ Updated AGENTS.md"
    else
        echo "⊘ Skipping AGENTS.md (already has Nowledge Mem section)"
    fi
fi

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Restart manicode in this project"
echo "2. Confirm trust when prompted for .agents/mcp.json"
echo "3. Or set FREEBUFF_TRUST_AGENTS=1 to skip confirmation"
echo ""
echo "To sync chat history:"
echo "  python3 $SCRIPT_DIR/tools/sync_chats.py --project-path $PROJECT_DIR"
