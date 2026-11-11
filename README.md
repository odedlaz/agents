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

- `external-audit` Prepare the PR with screening diffs, then run one Anthropic full-PR
  review for the broader review. After that review, finish with correction diffs only.
  Required findings use formal reviews with deduplicated inline comments; approval
  uses the private script. Models and settings live in
  [Reviewer configuration](skills/external-audit/SKILL.md#reviewer-configuration).
  The runtime must support the configured providers and settings; installing the
  plugin alone does not add delegation or model access.
- `self-improvement` Research and propose improvements to the user's local
  Claude Code instructions. This skill remains specific to Claude Code.

For direct skill installs, the audit commands are `/external-audit` and
`/xaudit` in Claude Code, or `$external-audit` and `$xaudit` in Codex. The
`xaudit` skill is a small alias that loads `external-audit`; it has no separate
review instructions.

Each review starts fresh without inherited conversation or earlier verdicts.
Preparation uses the screening profile: first actual PR base-to-head, then its
last completed screening SHA to current head. Once it accepts, only the Anthropic
deep profile reviews the entire PR at a pinned base/head. There is no OpenAI full
review. The full reviewer finishes the entire scope and collects all findings.

Record the completed Anthropic checkpoint even when it rejects. After that,
use only the OpenAI deep profile for correction diffs. The initial correction
baseline is the full-reviewed head; this does not claim earlier OpenAI coverage.
Later corrections use the last completed correction SHA to current head. Verify
all findings, including Anthropic findings outside the delta. Complete correction
acceptance with no open findings permits approval, without another Anthropic run.
If full review accepts unchanged code with no findings, approve directly.

Full review runs once per PR. Preserve its checkpoint and phase across sessions,
ordinary re-reviews, new commits and rebases. After a verified upstream merge or
rebase invalidates a cursor, review actual current base-to-head in the current
diff phase. After the checkpoint, this stays a correction diff. Only an explicit
request for another full review starts another cycle. A complete matching
Anthropic full result from a previous dual-review cycle can supply the checkpoint.
Fix code only when authorized; otherwise retain the phase and resume when fixes arrive.

Incomplete reviews retry fresh over the same assigned range, without advancing
cursors or completing a phase. If the PR moves during full review, finish/retry
its pinned snapshot, then cover new work with correction diffs. Preserve unpublished
findings and verify/reanchor them at the current head before publication. Partial
findings may publish without making coverage complete. The invocation authorizes
automatic reviews, transitions, retries, recovery and formal publication without
readiness or permission questions. Explicit user pauses apply.

Reuse approval only when current base/head, configured settings, phase coverage
and findings still match. A stale approval does not erase the full-review
checkpoint. Recheck current base/head before publication.

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
