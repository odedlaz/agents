# agents

Version-controlled home for my Claude Code global configuration. The real files
live here and are **symlinked** into `~/.claude/` so Claude Code finds them at the
paths it expects, while git tracks them here.

## Layout

```
agents/
├── CLAUDE.md                       # personal global instructions (all projects)
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
ln -sfn ~/Dev/agents/CLAUDE.md                ~/.claude/CLAUDE.md
ln -sfn ~/Dev/agents/skills/self-improvement  ~/.claude/skills/self-improvement
```

`-f` replaces an existing link; `-n` avoids nesting the link inside an existing
directory symlink. Run `ls -l ~/.claude/CLAUDE.md ~/.claude/skills/self-improvement`
to confirm both point back here.

## Notes

- **Moving this repo** is the one thing that breaks the links — re-run the setup
  commands above after relocating it.
- Adding a new global skill or config file? Drop it in this repo, then add a
  matching `ln -sfn` line above and to the setup block.
