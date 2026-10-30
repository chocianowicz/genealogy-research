#!/usr/bin/env sh
# Install the genealogy-research skill and its sub-agents for Claude Code (user scope).
# Usage: ./install.sh            -> ~/.claude/skills and ~/.claude/agents
#        ./install.sh <project>  -> <project>/.claude/skills and <project>/.claude/agents
set -eu
SRC=$(cd "$(dirname "$0")" && pwd)
BASE=${1:-$HOME}/.claude
mkdir -p "$BASE/skills/genealogy-research" "$BASE/agents"
cp -R "$SRC/SKILL.md" "$SRC/references" "$SRC/scripts" "$SRC/templates" "$BASE/skills/genealogy-research/"
cp "$SRC"/agents/*.md "$BASE/agents/"
echo "Installed skill -> $BASE/skills/genealogy-research"
echo "Installed agents -> $BASE/agents (archive-scout, film-mapper, scan-reader, evidence-auditor)"
