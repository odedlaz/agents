#!/usr/bin/env bash
# Link skills directly into Claude Code for local development.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$script_dir/link-skills.sh"
