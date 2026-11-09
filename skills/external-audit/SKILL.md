---
name: external-audit
description: Run an external audit with two adversarial PR reviewers, Claude Opus 5.5 and Codex Sol 6.1, when the user asks to "external-audit" a PR or invokes /external-audit. Each posts inline fixes; approve through the script only when both accept.
---

# External Audit

An invocation authorizes two adversarial subagent audits, each auditor posting
its own inline findings, and approval through the private script. Keep verdicts
and global feedback in chat. Do not implement changes or merge. Resolve the PR
URL from the request or unambiguous context; ask if the target is ambiguous.

## Start the auditors

Run exactly two fresh auditors in parallel:

- `claude-auditor` `claude-opus-5-5`, high reasoning effort, regular mode.
- `codex-auditor` `gpt-6.1-sol`, high reasoning effort, regular mode.

Resolve model IDs and supported options from runtime capabilities. Set these
configurations explicitly; do not substitute models or inherit settings that
could change effort or enable fast mode. If either is unavailable, report the
limitation and stop.

In T3 Code, use `orchestrator_capabilities` before the first `delegate_task`;
pass settings in `target.options` and follow returned continuation instructions.
Use supported delegation tools in other runtimes. Both auditors must start
without parent history, implementation context or previous review text.

Supply each only [the auditor prompt](references/auditor-prompt.md) unchanged,
repository location, PR URL, both review SHAs, reviewer identity and peer contact
or parent relay instructions. Both review the same range:

- `full-range` Initial or explicitly requested full review: real PR base to
  current head. For a stacked PR, use that layer's base.
- `delta-range` Re-review: previous reviewed head to current head. Retrieve the
  previous SHA from the review record; ask if unavailable rather than silently
  doing a full review. Record both SHAs in chat for the next re-review.

## Coordinate and decide

Each auditor first reads the code independently, then may exchange findings,
questions and counterexamples with its peer. Relay messages if direct contact
is unavailable, without adding implementation context. Discussion does not
require consensus; each verifies claims and keeps its own verdict. Each posts
its own final inline findings under the auditor prompt's rules and returns its
verdict, evidence, range and comment links. Do not consolidate their publications
into one parent review.

If either returns `REQUEST CHANGES`, that is the combined verdict. Missing
evidence, failed audits, ambiguous verdicts or publication failures cannot count
as acceptance. Report failures and unpublished findings in chat; clarify an
unsupported verdict rather than silently converting it.

Both must accept the same current head with no unresolved required findings
before approval. A delta verdict does not clear prior unresolved findings by
itself. Recheck the head before approval: if changed, cancel superseded audits
and start a fresh pair from the last reviewed SHA to the new head. An explicit
full-review request keeps the full PR range.

## Approve and report

Only the parent runs the approval script, once after both accept. Pass exactly
one argument, the PR URL, and pin the reviewed head. Resolve `approve` beside
this `SKILL.md` and use its absolute path as `APPROVE_SCRIPT_PATH`:

```sh
EXTERNAL_AUDIT_REVIEWED_HEAD='REVIEWED_HEAD_SHA' 'APPROVE_SCRIPT_PATH' 'https://github.com/OWNER/REPO/pull/NUMBER'
```

The script loads its own credentials. Do not read its adjacent `.env`, load
`~/.zshrc`, print credentials, or substitute another approval method. Do not post
an additional approval review or comment. After a failed or uncertain response,
check existing reviews before retrying and recheck the head to avoid duplicates
or approval of an unaudited commit.

Report both verdicts and the combined verdict in chat, with the reviewed range,
rationale, confidence, checks, limits and inline comment links. Include global
feedback and findings without valid inline locations. After script approval,
include its returned reviewer, commit and review link. Never post a top-level
GitHub comment, summary or `REQUEST_CHANGES` review on behalf of the auditors.
