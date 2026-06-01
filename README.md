# agents

Version-controlled home for my Claude Code global configuration. The real files
live here and are **symlinked** into `~/.claude/` so Claude Code finds them at the
paths it expects, while git tracks them here.

## Layout

```
agents/
├── CLAUDE.md                       # personal global instructions (all projects)
├── scripts/
│   └── link-skills.sh              # symlink skills/ into ~/.claude/skills/
└── skills/
    └── self-improvement/
        └── SKILL.md                # /self-improvement skill
```

## Symlinks

| Source of truth (this repo)                          | Symlink (where Claude Code reads it)        |
| ---------------------------------------------------- | ------------------------------------------- |
| `~/Dev/agents/CLAUDE.md`                             | `~/.claude/CLAUDE.md`                        |
| `~/Dev/agents/skills/self-improvement`               | `~/.claude/skills/self-improvement`          |

Edit files **here** (or through the symlink — same inode) and commit. Symlinks use
absolute targets, so they resolve from any working directory.

## Setup (fresh machine, or to restore the links)

```sh
ln -sfn ~/Dev/agents/CLAUDE.md ~/.claude/CLAUDE.md   # config file
./scripts/link-skills.sh                              # every skill in skills/
```

`-f` replaces an existing link; `-n` avoids nesting the link inside an existing
directory symlink. `link-skills.sh` symlinks each directory under `skills/` into
`~/.claude/skills/` (honoring `$CLAUDE_CONFIG_DIR`); it's idempotent, re-links stale
symlinks, and skips any real file already in the way. Run
`ls -l ~/.claude/CLAUDE.md ~/.claude/skills/` to confirm everything points back here.

## Notes

- **Moving this repo** is the one thing that breaks the links — re-run the setup
  commands above after relocating it.
- Adding a new global skill? Drop it under `skills/` and re-run
  `./scripts/link-skills.sh` — no README change needed.
- Adding a new config file (not a skill)? Add a matching `ln -sfn` line to the
  setup block above.
