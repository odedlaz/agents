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

- `external-audit` A fresh screening reviewer audits correction diffs. After complete
  acceptance, a fresh deep reviewer audits the entire PR. A rejection returns to
  authorized fixes and screening diffs, then another full review after screening
  accepts. Only full deep acceptance permits PAT-backed approval. Required findings
  use formal reviews with deduplicated inline findings. Models and settings live in
  [Reviewer configuration](skills/external-audit/SKILL.md#reviewer-configuration).
  Only OpenAI profiles are active; Anthropic rows remain for future configuration.
  The runtime must support the active provider and settings; installing the plugin
  alone does not add delegation or model access.
- `self-improvement` Research and propose improvements to the user's local
  Claude Code instructions. This skill remains specific to Claude Code.

For direct skill installs, the audit commands are `/external-audit` and
`/xaudit` in Claude Code, or `$external-audit` and `$xaudit` in Codex. The
`xaudit` skill is a small alias that loads `external-audit`; it has no separate
review instructions.

Each review starts fresh without inherited conversation or another reviewer's
conclusions. Screening first covers the actual PR base to head, then reviews its
own last completed screening SHA to the current head. Complete screening rejection
advances that cursor; partial reviews do not. Full reviews never advance the
screening cursor. Each full review covers the entire actual PR base-to-head range,
even after a previous full rejection. Match history by actual settings, audit mode
and coverage, not profile name. Preserve all open findings from older configurations.

Every reviewer finishes its assigned range and verifies all open findings,
including findings outside the screening diff. After a rejection, publish findings
and apply fixes only when authorized. Screening must accept again before another
full review. Approval requires complete acceptance from both active profiles at
the current base/head, including deep coverage of the entire PR.

The invocation authorizes the loop, retries, automatic full-review transition,
range recovery and formal reviews without further permission questions. After a
verified upstream merge or rebase invalidates the screening cursor or introduces
upstream changes, screen the actual current PR base-to-head diff. Deep still waits
for complete screening acceptance. Keep findings and retry incomplete work; report
concrete runtime blockers. Explicit user pauses apply. An explicit rescan restarts
screening at the actual PR base before the full review.

Reuse an existing published approval only when current base/head, active settings,
complete screening and full deep coverage, and open-finding records still match.
Explicit rescans rerun both stages. Otherwise retry only missing work while its
prerequisites remain valid.

Reviewers return independent verdicts and keep results compact. They batch related searches and focused reads, reuse retrieved evidence,
and expand inspection when needed. Stable prompt prefixes, tool definitions and
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
