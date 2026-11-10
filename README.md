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

- `external-audit` One reviewer handles screening and correction diffs. After it
  accepts, a fresh reviewer checks the entire PR before approval. Both stages use
  the configured Anthropic profiles. Required findings are published through one
  PAT-backed review with deduplicated inline findings. Models and settings live in
  [Reviewer configuration](skills/external-audit/SKILL.md#reviewer-configuration).
  The OpenAI table entries are retained for future use and do not run. The runtime
  must support the active provider and settings; installing the plugin alone does
  not add delegation or model access.
- `self-improvement` Research and propose improvements to the user's local
  Claude Code instructions. This skill remains specific to Claude Code.

For direct skill installs, the audit commands are `/external-audit` and
`/xaudit` in Claude Code, or `$external-audit` and `$xaudit` in Codex. The
`xaudit` skill is a small alias that loads `external-audit`; it has no separate
review instructions.

The active screening and final profiles use the same model and effort. Profile
names identify stages. Each review starts fresh without inherited conversation or
prior conclusions. Model IDs and settings live only in the table linked above.

Initial screening covers the entire PR. Correction diffs use the last completed
screening/correction SHA, including one from the previous provider when the
workflow changes. Preserve open findings and coverage records when changing profiles.
After screening accepts the current base and head, a fresh final reviewer checks
the entire PR. Its acceptance is required even when initial screening passes
immediately. Every reviewer finishes the assigned scope and collects all required
findings before a normal verdict. A completed rejection publishes findings, then
returns to authorized fixes and correction diffs. After screening accepts again,
start a fresh final-full cycle. Partial reviews never advance cursors or approve.

The invocation authorizes both review stages, retries, range recovery and review
publication without further permission questions. Incomplete screening keeps
retrying the screening profile; no retry count bypasses acceptance. After a verified
upstream merge or rebase expands the correction range, review the actual current
PR base-to-head range at the screening stage and retain open findings. Report a
concrete runtime blocker without bypassing the gate. Explicit user pauses apply.

An explicit full audit reruns screening over the entire PR, then the fresh final
review after acceptance. Unchanged ranges reuse results only within their stage;
screening never replaces final-full review. Reuse an existing published approval
only when current base/head, active settings and complete screening and final
records match, with no open required findings. Required findings stay open until
verified corrections close them.

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
