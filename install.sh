#!/bin/bash
# install.sh - Install nowledge-mem-freebuff into a project

set -e

PROJECT_PATH="${1:-.}"

if [ ! -d "$PROJECT_PATH" ]; then
    echo "ERROR: Project path not found: $PROJECT_PATH"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$PROJECT_PATH" && pwd)"

echo "Installing Nowledge Mem for freebuff into: $PROJECT_DIR"

# 1. Create .agents directory
mkdir -p "$PROJECT_DIR/.agents/skills/nowledge-mem"

# 2. Copy MCP config
if [ ! -f "$PROJECT_DIR/.agents/mcp.json" ]; then
    cp "$SCRIPT_DIR/mcp/mcp.json.example" "$PROJECT_DIR/.agents/mcp.json"
    echo "✓ Created .agents/mcp.json"
else
    echo "⊘ Skipping .agents/mcp.json (already exists)"
fi

# 3. Copy skills
for skill_dir in read-working-memory search-memory distill-memory save-thread status; do
    if [ ! -f "$PROJECT_DIR/.agents/skills/nowledge-mem/$skill_dir/SKILL.md" ]; then
        mkdir -p "$PROJECT_DIR/.agents/skills/nowledge-mem/$skill_dir"
        cp "$SCRIPT_DIR/skills/$skill_dir/SKILL.md" "$PROJECT_DIR/.agents/skills/nowledge-mem/$skill_dir/SKILL.md"
        echo "✓ Created .agents/skills/nowledge-mem/$skill_dir/SKILL.md"
    else
        echo "⊘ Skipping $skill_dir (already exists)"
    fi
done

# 4. Create or update AGENTS.md
if [ ! -f "$PROJECT_DIR/AGENTS.md" ]; then
    cp "$SCRIPT_DIR/AGENTS.md" "$PROJECT_DIR/AGENTS.md"
    echo "✓ Created AGENTS.md"
else
    if ! grep -q "Nowledge Mem for freebuff" "$PROJECT_DIR/AGENTS.md"; then
        cat >> "$PROJECT_DIR/AGENTS.md" << 'EOF'

---

## Nowledge Mem for freebuff

You have access to the user's cross-tool knowledge through the `nmem` CLI and five installed skills.

See the full guide at `.agents/skills/nowledge-mem/`.
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
echo "1. Restart freebuff in this project"
echo "2. When prompted, trust the .agents/mcp.json configuration"
echo "   OR set env: export FREEBUFF_TRUST_AGENTS=1"
echo ""
echo "To sync chat history:"
echo "  knowledge-mem-freebuff-sync --project <project_name> --apply"
echo ""
echo "Available sync options:"
echo "  knowledge-mem-freebuff-sync --help"
