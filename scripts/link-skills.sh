#!/usr/bin/env bash
#
# Symlink every skill in this repository's skills/ directory into ~/.claude/skills/
# so they are picked up globally by Claude Code. Idempotent and safe to re-run.

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src_dir="$repo_root/skills"
dest_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"

if [[ ! -d "$src_dir" ]]; then
  echo "No skills directory found at $src_dir" >&2
  exit 1
fi

mkdir -p "$dest_dir"

for skill_path in "$src_dir"/*/; do
  [[ -d "$skill_path" ]] || continue

  skill_name="$(basename "$skill_path")"
  skill_path="${skill_path%/}"
  link_path="$dest_dir/$skill_name"

  if [[ -L "$link_path" ]]; then
    if [[ "$(readlink "$link_path")" == "$skill_path" ]]; then
      echo "ok      $skill_name (already linked)"
      continue
    fi
    ln -sfn "$skill_path" "$link_path"
    echo "relink  $skill_name"
  elif [[ -e "$link_path" ]]; then
    echo "skip    $skill_name (a non-symlink already exists at $link_path)" >&2
    continue
  else
    ln -s "$skill_path" "$link_path"
    echo "link    $skill_name"
  fi
done
