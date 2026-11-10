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

- `external-audit` One shallow reviewer handles initial screening and correction diffs.
  Two independent deep reviewer roles, `openai` and `anthropic`, run final full reviews
  in parallel. Either role can require corrections through
  one PAT-backed review with deduplicated inline findings. Approval requires both
  roles to pass a separate final full review of the same commit. Reviewer models
  and settings are configured only in
  [Reviewer configuration](skills/external-audit/SKILL.md#reviewer-configuration).
  This workflow requires a runtime that can delegate to both configured providers,
  such as T3 Code; plugin installation alone does not add delegation or model access.
- `self-improvement` Research and propose improvements to the user's local
  Claude Code instructions. This skill remains specific to Claude Code.

For direct skill installs, the audit commands are `/external-audit` and
`/xaudit` in Claude Code, or `$external-audit` and `$xaudit` in Codex. The
`xaudit` skill is a small alias that loads `external-audit`; it has no separate
review instructions.

The `openai` role uses its shallow profile alone for initial screening and correction
diffs. Both roles use their deep profiles for final full reviews after shallow acceptance.
Model IDs and effort settings live only in the table
linked above. Profile switches preserve each provider role's review history.

Initial screening covers the full PR. Correction diffs use the `openai` role's own
last completed review head, including completed reviews that did not publish.
Once screening accepts, two fresh deep reviewers automatically review the entire
PR in parallel before approval. This stage is required even when initial screening
passes immediately. A confirmed required final finding rejects the cycle early:
stop the unfinished peer, publish deduplicated findings, then return to fixes and
single-reviewer diffs. After screening accepts again, start a new final full cycle.
Partial or cancelled reviews do not advance cursors or count as approval. Both
final reviewers must complete and accept the current PR base and head before the
approval script runs.

The invocation authorizes the entire review loop without further permission questions.
Incomplete screening or correction diffs keep retrying with the shallow profile;
no retry count permits deep escalation. After a verified upstream merge or rebase
expands the correction range, use the actual current PR base-to-head range with
the shallow profile. Keep its open-finding checklist and retry that corrected range.
A concrete runtime blocker is reported, without bypassing shallow acceptance.
An explicit user pause still applies.

An explicit full-audit request resets the shallow screening range to the entire PR;
it does not bypass the shallow gate. Both deep profiles start only after complete
shallow acceptance for the current PR base and head. Unchanged ranges reuse results
only within the same stage; shallow results never replace final full results.
Required findings remain open until their corrections are verified.

Reviewers return independent verdicts without routine peer debate and keep results
compact. They use bounded code reads, expand inspection when evidence requires it,
and receive stable instructions before changing task details to support prompt
caching where the runtime permits. These controls do not guarantee token savings.

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
