#!/usr/bin/env bash
# Install framework skills/agents into tool-specific locations.
#
# Usage:
#   ./t-shirt-size-install.sh [claude|cursor|codex|all]   # default: all
#
# Re-run after editing skills/ or agents/ to propagate changes.
# Existing target dirs are replaced (not merged).

set -euo pipefail

TARGET="${1:-all}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

[ -d skills ] || { echo "Error: skills/ not found in $SCRIPT_DIR" >&2; exit 1; }

install_dir() {
    local target="$1"
    local source="$2"
    rm -rf "$target"
    mkdir -p "$(dirname "$target")"
    cp -R "$source" "$target"
    echo "  ✓ $target"
}

install_claude() {
    echo "Claude Code:"
    install_dir .claude/skills skills
    if [ -d agents ]; then
        install_dir .claude/agents agents
    fi
}

install_cursor() {
    echo "Cursor:"
    install_dir .cursor/skills skills
    if [ -d agents ]; then
        install_dir .cursor/agents agents
        echo "  ⚠ Cursor agents use different frontmatter (no 'tools' field; model values differ)."
        echo "    Review .cursor/agents/ and adjust if delegation doesn't work as expected."
    fi
}

install_codex() {
    echo "Codex:"
    install_dir .agents/skills skills
    if [ -d agents ]; then
        echo "  ⚠ Codex subagents are TOML user-level only (~/.codex/agents/)."
        echo "    Not copied. Translate manually if you need them in Codex."
    fi
}

case "$TARGET" in
    claude) install_claude ;;
    cursor) install_cursor ;;
    codex)  install_codex ;;
    all)    install_claude; install_cursor; install_codex ;;
    -h|--help)
        sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'
        exit 0
        ;;
    *)
        echo "Unknown target: $TARGET" >&2
        echo "Usage: $0 [claude|cursor|codex|all]" >&2
        exit 1
        ;;
esac

echo ""
echo "Done. AGENTS.md and CLAUDE.md at repo root are read natively by all three tools — no copy needed."
