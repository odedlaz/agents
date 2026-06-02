# Personal preferences (apply in every project on this machine)

## Working approach

- **Scope before building, then run with it.** Plan non-trivial work — explore the relevant code, propose a short plan, confirm direction — and for large or ambiguous features, interview with `AskUserQuestion` (implementation, UX, edge cases, tradeoffs) and write a short spec rather than guessing. Trivial/mechanical edits skip this. Pairs with the no-auto-commit checkpoint below.

- **Explore with read-only subagents.** For broad "where/how does X work" searches across many files, spin up exploration subagents (e.g. the Explore agent) and bring back the conclusions, rather than reading lots of files into the main context. Keeps the working context lean.

- **Keep context lean.** Prefer `@`-mentions and symbol/LSP search over reading whole files; read only the part of a file I actually need. Load skills on demand rather than front-loading them.

- **Reserve multi-agent workflows for large, high-stakes work.** Reach for dynamic workflows only for codebase-wide audits, large migrations, or verification-critical tasks — and scope them, since they consume substantially more tokens than a normal session. Don't use them for routine edits.

- **Verify by running, not by asserting.** Don't claim a change works without evidence — a test run, an app run, observed output. Report failures with the actual output, and say plainly when something is unverified or a step was skipped.

- **Capture corrections.** When the user corrects me or states a durable preference, proactively record it — to memory, or the relevant `CLAUDE.md` — so I don't repeat the mistake. ("Compounding engineering.")

- **Delegation over hand-holding.** Treat a crisp brief as a delegation: do the work and report back when done or when there's a real blocking question — rather than narrating every step and asking frequently. Ask up front only when the request is genuinely ambiguous.

- **Fix root causes, not symptoms.** Never mask a failure — don't swallow exceptions, silence a linter/type error, or hardcode around a broken path. Diagnose the underlying cause and fix that.

- **Step back after repeated failure.** If the same problem fails ~twice, stop retrying in a polluted context: reconsider the approach from scratch and surface the blocker, rather than piling on more attempts. Likewise, when a fix merely works but feels mediocre, prefer a cleaner solution over shipping the first thing that passes.

## Commits & git

- **Never auto-commit.** Don't run `git add`/`git commit` without explicit per-commit confirmation — even when prior instructions implied a commit-friendly cadence. After making changes, run type-check/tests, then stop, summarize what changed, and wait for an explicit "commit". Same for `git push` (explicit-only) and for squash/amend/split decisions (ask, don't assume). Deliberately-invoked commands like `/commit` are fine.

- **No Claude attribution.** Omit the "🤖 Generated with [Claude Code](https://claude.com/claude-code)" footer from PR bodies, and omit the `Co-Authored-By: Claude ...` trailer from commit messages. Applies to amends and follow-up commits, not just the first.

- **Always use a worktree.** Do the work in a dedicated `git worktree` rather than switching branches in the primary checkout — keep the main working tree clean and the task isolated.

## Code quality

- **Clean Code is the standing bar.** Apply *Clean Code* / *The Clean Coder* principles continuously while writing, not just on a review pass — readability over cleverness, tests first. Boy Scout Rule scoped to what I'm touching; every commit a coherent, working increment (type-check + tests green, never WIP/broken).

## File output format

- **Choose format by who renders the file.** Inside a git repo, use GitHub-flavored Markdown for `.md` files — GitHub sanitizes inline HTML, so rich HTML renders broken (READMEs, `/docs`, wikis, issue/PR bodies). Otherwise — opened in a browser or shared outside GitHub — prefer self-contained HTML. [Rationale](https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html)
