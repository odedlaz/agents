# Personal preferences (apply in every project on this machine)

## Working approach

- **Plan before coding on non-trivial work.** Explore and understand the relevant code first, propose a short plan, confirm direction, then implement. Trivial/mechanical edits don't need this. Pairs with the no-auto-commit checkpoint below.

- **Explore with read-only subagents.** For broad "where/how does X work" searches across many files, spin up exploration subagents (e.g. the Explore agent) and bring back the conclusions, rather than reading lots of files into the main context. Keeps the working context lean.

- **Keep context lean.** Prefer `@`-mentions and symbol/LSP search over reading whole files; read only the part of a file I actually need. Load skills on demand rather than front-loading them.

- **Reserve multi-agent workflows for large, high-stakes work.** Reach for dynamic workflows only for codebase-wide audits, large migrations, or verification-critical tasks — and scope them, since they consume substantially more tokens than a normal session. Don't use them for routine edits.

- **Verify by running, not by asserting.** Don't claim a change works without evidence — a test run, an app run, observed output. Report failures with the actual output, and say plainly when something is unverified or a step was skipped.

- **Capture corrections.** When the user corrects me or states a durable preference, proactively record it — to memory, or the relevant `CLAUDE.md` — so I don't repeat the mistake. ("Compounding engineering.")

- **Self-critique before declaring done.** Be honest about uncertainty, catch my own bugs before claiming victory, and when a fix feels mediocre, reconsider for a cleaner solution rather than shipping the first thing that works.

- **Delegation over hand-holding.** Treat a crisp brief as a delegation: do the work and report back when done or when there's a real blocking question — rather than narrating every step and asking frequently. Ask up front only when the request is genuinely ambiguous.

- **Interview before big features.** For large or ambiguous features, use `AskUserQuestion` to interview the user about implementation, UX, edge cases, and tradeoffs, and write a short spec before coding — rather than guessing and building the wrong thing.

- **Fix root causes, not symptoms.** Never mask a failure — don't swallow exceptions, silence a linter/type error, or hardcode around a broken path. Diagnose the underlying cause and fix that.

- **Step back after repeated failure.** If the same problem fails ~twice, stop retrying in a polluted context: reconsider the approach from scratch and surface the blocker, rather than piling on more attempts.

## Commits & git

- **Never auto-commit.** Don't run `git add`/`git commit` without explicit per-commit confirmation — even when prior instructions implied a commit-friendly cadence. After making changes, run type-check/tests, then stop, summarize what changed, and wait for an explicit "commit". Same for `git push` (explicit-only) and for squash/amend/split decisions (ask, don't assume). Deliberately-invoked commands like `/commit` are fine.

- **No Claude attribution.** Omit the "🤖 Generated with [Claude Code](https://claude.com/claude-code)" footer from PR bodies, and omit the `Co-Authored-By: Claude ...` trailer from commit messages. Applies to amends and follow-up commits, not just the first.

- **No "Closes" suffix in PRs.** Don't add `Closes NEO-N` / `Fixes #N` / `Resolves ...` trailers to PR descriptions. (A ticket ID in the commit/PR *title* is fine where a repo requires it — just not a closing suffix in the body.)

## Code quality

- **Clean Code is the standing bar for everything committed.** Hold Robert C. Martin's *Clean Code* / *The Clean Coder* principles while writing, in every repo — not just on an on-demand review pass. Each commit is a coherent, working increment (type-check + tests green; never WIP/broken). Boy Scout Rule, scoped to what I'm already touching.
  - **Names** reveal intent; no type/scope encodings; replace magic numbers/strings with named constants.
  - **Functions** small, one thing, one level of abstraction, few args, no boolean/flag params (split instead), no hidden side effects.
  - **Comments**: prefer self-documenting code; comment *why* not *what*; never leave commented-out code.
  - **DRY** but not over-abstracted — YAGNI beats premature generalization; the wrong abstraction costs more than duplication.
  - **SOLID** + Law of Demeter; prefer polymorphism / lookup maps over sprawling type-switch chains.
  - **Tests** are F.I.R.S.T. and written test-first.
  - Readability over cleverness/brevity, always.

- **Prefer `const` over `let` in TypeScript.** Treat `let` as a code smell needing justification. After writing, scan for `let` and ask whether a single-expression form fits:
  - `let x; if (c) x=a; else x=b;` → `const x = c ? a : b;`
  - pre-declared + filled in try/catch → a single `const = (() => { try {...} catch (err) {...} })()` IIFE, or a helper
  - `let acc=[]; for(...) acc.push(...)` → `const acc = items.flatMap(...)` / `.map(...)` / `.reduce(...)`
  - Legitimate `let` (don't churn): counters mutated across async callbacks where parallelism blocks a clean reduce; genuine sequential state where each step depends on the prior and no functional form is cleaner.
  - When in doubt, prefer `const` + a small helper over `let` + branching mutation.

## File output format

- **Decide by who renders the file.**
  - **Inside a git repository → use GitHub-flavored Markdown for `.md` files.** GitHub sanitizes HTML in Markdown (strips `<script>`, `<style>`, inline `style=`, classes, inline `<svg>`), so rich HTML renders broken there. GFM already covers most needs: native tables, ` ```mermaid ` diagrams, `$LaTeX$` math, `<details>`/`<summary>` collapsibles, `> [!NOTE]`/`> [!WARNING]` callouts, task lists, footnotes. This applies to anything the GitHub renderer processes — READMEs, `/docs`, wikis, issue/PR bodies.
  - **Standalone artifact opened directly in a browser or shared outside GitHub → prefer rich, self-contained HTML.** For specs, plans, design/code reviews, reports, mockups — especially once content gets non-trivial (~100+ lines) or benefits from styled layout, SVG/diagrams, or interactive bits (sliders, forms, copy-as-JSON/prompt buttons). Make it self-contained (inline CSS/JS, no external deps) and mobile-responsive. Rationale: https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html

## macOS

- **Open links in Chrome's work profile.** For work URLs (GitHub, Notion, dashboards, docs) use Google Chrome's work profile — not the default browser or Chrome's default profile (work URLs need the work profile's sign-in cookies). On this machine the work profile is named **`neo`** and lives in Chrome's `Default` directory. Use:

  ```sh
  open -na "Google Chrome" --args --profile-directory="Default" <url>
  ```

  `-n` forces a new instance so the requested profile is honored.
