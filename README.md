# Agents

Personal skills distributed as a `skills` plugin in the `odedlaz` marketplace for Claude Code and Codex.
Both clients load the same `skills/` directory. The GitHub repository remains
`odedlaz/agents`.

## Install in Claude Code

```sh
claude plugin marketplace add odedlaz/agents
claude plugin install skills@odedlaz
```

Start a new session, then invoke `/skills:external-audit` or `/skills:xaudit`.
Both run the same external audit. `/skills:self-improvement` is also available.

## Install in Codex

```sh
codex plugin marketplace add odedlaz/agents
codex plugin add skills@odedlaz
```

Start a new session and invoke `$external-audit` or `$xaudit`, or select the skill
from the plugin's skill picker. Both names run the same external audit.

## Skills

- `external-audit` Start with one independent initial full review. Resolve findings
  through contextual preparation diffs, then run one independent Anthropic full
  review. Resolve its findings through contextual correction diffs and approve.
  A clean full verdict skips its diff loop. Required findings use formal inline
  reviews; approval uses the private script. Models and settings live in
  [Reviewer configuration](skills/external-audit/SKILL.md#reviewer-configuration).
  The runtime must support the configured providers and settings.
- `self-improvement` Research and propose improvements to the user's local
  Claude Code instructions. This skill remains specific to Claude Code.

For direct skill installs, the audit commands are `/external-audit` and
`/xaudit` in Claude Code, or `$external-audit` and `$xaudit` in Codex. The
`xaudit` skill is a small alias that loads `external-audit`; it has no separate
review instructions.

Each review starts fresh. Both full stages receive only the prompt, repository/PR,
profile, audit mode and range metadata, with no inherited conversation, task or
implementation narrative, previous verdicts or finding checklist. They review the
entire launch-time pinned PR base-to-head range. The parent retains historical
findings that a fresh full reviewer was not given; they need explicit verification.

Diff reviewers receive the problem, requirements, intended fix, rationale and
prior findings, including evidence and closure conditions. They verify claims
against code. Preparation diffs start at the completed initial full-review head;
correction diffs start at the completed Anthropic full-review head. Later diffs
use their own phase's last completed review SHA. Verify all findings, including
those outside the delta. Complete diff acceptance advances to the next full stage
or approval, according to the saved phase.

Each full stage runs once per PR. A complete rejection records its checkpoint and
leads to contextual diff reviews, not another full run. A clean initial full review
moves directly to Anthropic. A clean Anthropic review permits approval directly.
After Anthropic findings, correction acceptance with every finding closed permits
approval without another full review. Fix code only when authorized.

Preserve checkpoints and phase across sessions, re-reviews, new commits and rebases.
A valid existing Anthropic checkpoint from an older workflow continues directly
in corrections; do not retroactively insert the new initial stage. A verified
upstream merge or rebase that invalidates a diff cursor uses actual current PR
base-to-head in the current diff phase. Only an explicit request for another full
review resets a completed stage.

Incomplete reviews retry fresh over the same range with the mode's context policy.
They do not advance cursors, permit fixes or complete a phase. In-flight full reviews
finish their pinned snapshots even if the PR moves; the next diff phase covers new
work and verifies/reanchors unpublished findings at current head. The invocation
authorizes automatic stages, retries, range recovery and formal publication without
readiness or permission questions. Explicit user pauses apply.

Reuse approval only when current base/head, settings, phase coverage and findings
still match. Recheck base/head before publication. Models and effort are configured
only in the skill table.

Reviewers return independent verdicts and keep results compact. They batch related searches and focused reads, reuse retrieved evidence,
and expand inspection when needed. Mode-specific context stays after stable prompt prefixes. Tool definitions and
tool order support caching where the runtime permits. If configurable, cache
lifetime follows expected reuse intervals and recorded usage; the skill does not
invent cache controls or reduce reasoning effort. Supported tool discovery, filtered
tool results and context management can reduce overhead. See the
[runtime cost controls](skills/external-audit/references/cost-controls.md).
These controls do not guarantee token savings.

## Review credentials and scripts

`external-audit/approve` and `external-audit/request-changes` load `API_KEY`
from the same adjacent `.env`. The PAT needs **Pull requests: Read and write**
on the target repositories and must belong to an account other than the PR
author. Configure `.env` separately in each installed copy; it is ignored by git
and not shipped in the marketplace. Reviewers never load the credentials.

Both scripts require GitHub CLI (`gh`); `request-changes` also requires `jq`.
Run `approve` with the PR URL and `EXTERNAL_AUDIT_REVIEWED_HEAD` set to the
reviewed SHA. Run `request-changes` with the PR URL and a JSON file path, or `-`
for stdin. The JSON requires `commit_id`, `body`, and optionally `comments` with
`path`, `line`, `side`, and `body` for each inline finding. The script sets
`event` to `REQUEST_CHANGES` and rejects a changed head, self-review, or exact
duplicate inline comment objects. The parent removes semantic duplicates
before calling the script.

```sh
./skills/external-audit/request-changes https://github.com/OWNER/REPO/pull/123 review.json
```

The [skill instructions](skills/external-audit/SKILL.md) include a JSON example.
The payload follows GitHub's [create-review API](https://docs.github.com/en/rest/pulls/reviews#create-a-review-for-a-pull-request).

## Local development

Register a checkout instead of GitHub by passing its absolute path to
`claude plugin marketplace add` or `codex plugin marketplace add`.

For direct Claude skill links, `./scripts/setup.sh` links every skill into
`${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/`. It does not manage global instruction
files. Avoid installing both direct links and the plugin in the same client.

```sh
python3 -m unittest discover -s scripts/__tests__ -v
claude plugin validate .
claude plugin validate .claude-plugin/marketplace.json
codex plugin list --marketplace odedlaz --available --json
```

Update the plugin version in both manifests when publishing changes.
Marketplace formats follow the [Claude Code marketplace reference](https://code.claude.com/docs/en/plugin-marketplaces)
and [Codex plugin packaging documentation](https://developers.openai.com/plugins/build/plugins).
