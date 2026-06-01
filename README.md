# agents

Version-controlled home for my Claude Code global configuration. The shared files
live here and are **symlinked** into `~/.claude/` so Claude Code finds them at the
paths it expects, while git tracks them here.

Global instructions use a two-layer split:

- **`CLAUDE.md` (this repo)** — shared instructions for every machine. Symlinked to
  `~/.claude/REMOTE.md`.
- **`~/.claude/CLAUDE.md` (local, not tracked)** — a thin file that imports the shared
  layer with `@~/.claude/REMOTE.md`, then adds machine-specific preferences below it.
  This is the file Claude Code actually loads; the import pulls in the shared layer.

## Layout

```
agents/
├── CLAUDE.md                       # shared global instructions (symlinked to ~/.claude/REMOTE.md)
├── scripts/
│   ├── setup.sh                    # full setup: REMOTE.md symlink + local CLAUDE.md + skills
│   └── link-skills.sh              # symlink skills/ into ~/.claude/skills/
└── skills/
    └── self-improvement/
        └── SKILL.md                # /self-improvement skill
```

## Symlinks

| Source of truth (this repo)            | Symlink (where Claude Code reads it) |
| -------------------------------------- | ------------------------------------ |
| `~/Dev/agents/CLAUDE.md`               | `~/.claude/REMOTE.md`                |
| `~/Dev/agents/skills/self-improvement` | `~/.claude/skills/self-improvement`  |

`~/.claude/CLAUDE.md` is **not** a symlink — it's a local, untracked file that imports
`~/.claude/REMOTE.md` and holds this machine's own preferences. Edit shared instructions
**here** (or through the `REMOTE.md` symlink — same inode) and commit; edit
machine-specific ones directly in `~/.claude/CLAUDE.md`. Symlinks use absolute targets,
so they resolve from any working directory.

## Setup (fresh machine, or to restore the links)

```sh
./scripts/setup.sh
```

`setup.sh` (a) symlinks `~/.claude/REMOTE.md` to this repo's `CLAUDE.md`, (b) creates a
fresh `~/.claude/CLAUDE.md` that imports it — only if one doesn't already exist, so local
preferences are never clobbered — and (c) runs `link-skills.sh` to symlink every directory
under `skills/` into `~/.claude/skills/`. It honors `$CLAUDE_CONFIG_DIR`, is idempotent,
and is safe to re-run. Run `ls -l ~/.claude/REMOTE.md ~/.claude/skills/` to confirm
everything points back here.

## Notes

- **Moving this repo** is the one thing that breaks the links — re-run
  `./scripts/setup.sh` after relocating it.
- Adding a new global skill? Drop it under `skills/` and re-run `./scripts/setup.sh`
  (or `./scripts/link-skills.sh`) — no README change needed.
- Machine-specific instructions go in `~/.claude/CLAUDE.md`, below the import — not in
  the tracked `CLAUDE.md`.
