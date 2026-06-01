#!/usr/bin/env bash
#
# Set up this repository's global Claude Code config on a machine:
#   1. symlink ~/.claude/REMOTE.md -> this repo's CLAUDE.md   (shared, version-controlled)
#   2. create a fresh ~/.claude/CLAUDE.md that imports REMOTE.md   (local, machine-specific)
#   3. symlink every skill via link-skills.sh
#
# Idempotent and safe to re-run: it re-links REMOTE.md and never clobbers an
# existing local CLAUDE.md (which holds machine-specific preferences).

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
config_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

mkdir -p "$config_dir"

# 1. Shared config: REMOTE.md -> repo CLAUDE.md
remote_link="$config_dir/REMOTE.md"
remote_target="$repo_root/CLAUDE.md"
ln -sfn "$remote_target" "$remote_link"
echo "link    REMOTE.md -> $remote_target"

# 2. Local config: a fresh CLAUDE.md that imports REMOTE.md (only if absent)
local_config="$config_dir/CLAUDE.md"
if [[ -e "$local_config" || -L "$local_config" ]]; then
  echo "skip    CLAUDE.md (already exists; leaving local preferences untouched)"
else
  cat > "$local_config" <<'EOF'
@~/.claude/REMOTE.md

# Local-only preferences (this machine, not shared via the agents repo)
EOF
  echo "create  CLAUDE.md (imports REMOTE.md)"
fi

# 3. Skills
"$script_dir/link-skills.sh"
