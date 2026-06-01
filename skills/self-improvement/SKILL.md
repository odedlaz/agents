---
name: self-improvement
description: Use when the user wants to refresh or improve their global ~/.claude/CLAUDE.md from the latest Claude Code best practices. Surveys the sources below, proposes behavioral additions, and applies the approved ones. Triggers on "improve my CLAUDE.md", "check for new Claude Code best practices", or "/self-improvement".
---

# Self-Improvement

Survey authoritative sources on using Claude Code well, then propose a **small, high-signal** set of standing behavioral rules for the user's global `~/.claude/CLAUDE.md`. Approve before writing — never auto-apply.

## Sources

The user maintains this list — add bullets below and they're picked up automatically. Notes say how to fetch each (X resists direct fetch → WebSearch).

- Claude blog: https://claude.com/blog — scan for Claude Code / engineering / agents posts, fetch the relevant ones.
- Boris Cherny (creator): X https://x.com/bcherny via WebSearch `bcherny Claude Code tips`; mirror https://howborisusesclaudecode.com/.
- Anthropic official: https://code.claude.com/docs/en/best-practices + https://www.anthropic.com/engineering/claude-code-best-practices — canonical, fetches reliably.
- Cat Wu (Head of Product, Claude Code): X https://x.com/_catwu via WebSearch `Cat Wu _catwu Claude Code tips`.
- Jesse Vincent (creator of "Superpowers" skills): blog https://blog.fsck.com (X @obra, unverified).
<!-- Add more sources below this line -->

## Steps

1. Read `~/.claude/CLAUDE.md` (and the project `MEMORY.md` index if present) to know what already exists.
2. Survey the sources above in parallel; extract concrete recommendations.
3. **Keep only standing behavioral rules for Claude.** Exclude: personal setup (sessions, worktrees, terminal, models); harness config (permissions, hooks, MCP, sandbox → `settings.json`); repo-specific conventions (→ repo `CLAUDE.md` PR); anything already in the file or enforced by the harness.
4. De-dupe, then phrase each survivor as one crisp rule (bold lead-in + a sentence) matching the file's style.
5. Present candidates with one-line rationales; separately note the excluded items and why. Use `AskUserQuestion` (multiSelect, ≤4 options/question) to let the user choose.
6. Apply approved items into the best-fitting existing section, preserving structure.
7. Summarize what changed, cite sources as links, and remind the user to skim for redundancy.

Keep the bar high: a global rule fires on every task in every project. When unsure, leave it out and mention it as optional. Offer genuinely repo-specific finds as a repo-`CLAUDE.md` PR instead.
