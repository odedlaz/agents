---
name: external-audit
description: Run an external audit with two adversarial PR reviewers, Claude Opus 5.5 and Codex Sol 6.1, when the user asks to "external-audit" a PR or invokes /external-audit. Publish one PAT-backed GitHub review with inline findings; request changes only for mutually agreed findings, or approve only when both accept.
---

# External Audit

An invocation authorizes two adversarial subagent audits and one PAT-backed
GitHub review through the private scripts. Findings belong inside the review,
not standalone comments. Keep verdict explanations and global feedback in chat.
Do not implement changes or merge. Resolve the PR URL from the request or
unambiguous context; ask if the target is ambiguous.

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

Each auditor first reads the code independently, then both exchange findings,
questions and counterexamples. Relay messages if direct contact is unavailable,
without adding implementation context. Each verifies the other's claims against
the code. Neither publishes directly.

Reconcile the findings into one canonical list. Merge reports of the same
underlying defect even when their wording, slugs or nearby line anchors differ;
keep genuinely distinct defects separate, including those on the same line.
Assign one stable slug and one inline comment per defect.

Both auditors must explicitly confirm the same final list, including evidence,
severity, locations and required corrections, for the same reviewed head before
calling `request-changes`. Agreement on the verdict alone is insufficient.
Record both confirmations in chat. Do not force agreement or silently discard
supported objections. If a disagreement remains, publish neither a change
request nor an approval; report the disputed findings and evidence in chat.

If both agree that required work remains, the combined verdict is
`REQUEST CHANGES`. Missing evidence, failed audits, ambiguous verdicts or
publication failures cannot count as acceptance. Report failures and unpublished
findings in chat; clarify an unsupported verdict rather than converting it.

Both must accept the same current head with no unresolved required findings
before approval. A delta verdict does not clear prior unresolved findings by
itself. Recheck the head before approval: if changed, cancel superseded audits
and start a fresh pair from the last reviewed SHA to the new head. An explicit
full-review request keeps the full PR range.

## Publish and report

Only the parent runs the private scripts. Resolve `approve` and
`request-changes` beside this `SKILL.md` and use their absolute paths.

For `REQUEST CHANGES`, write a JSON file containing the reviewed `commit_id`,
a short neutral `body`, and `comments` with all required inline findings from
the agreed canonical list. Include each finding once. Each comment needs
`path`, `line`, `side` (LEFT or RIGHT), and `body` with its slug, severity, evidence, impact and required correction or
proof. Preserve real newlines; do not invent diff locations. Keep findings
without valid inline locations in chat; they still require changes. The
`comments` array may be empty in that case.

```json
{
  "commit_id": "REVIEWED_HEAD_SHA",
  "body": "Please address the required findings.",
  "comments": [
    {
      "path": "src/example.ts",
      "line": 42,
      "side": "RIGHT",
      "body": "`finding-slug` Major: evidence, impact, and required correction."
    }
  ]
}
```

```sh
'REQUEST_CHANGES_SCRIPT_PATH' 'https://github.com/OWNER/REPO/pull/NUMBER' 'REVIEW_JSON_PATH'
```

`request-changes` also accepts `-` as the JSON path to read stdin. It pins the
review to `commit_id`, checks the current head, and submits `REQUEST_CHANGES`
with all inline comments in one review. It rejects exact duplicate comment
objects as a final guard; semantic deduplication belongs to the reconciliation
above. It never submits a standalone comment.

Only when both auditors accept the same current head with no unresolved required
findings, run `approve` once with exactly one argument, the PR URL:

```sh
EXTERNAL_AUDIT_REVIEWED_HEAD='REVIEWED_HEAD_SHA' 'APPROVE_SCRIPT_PATH' 'https://github.com/OWNER/REPO/pull/NUMBER'
```

Both scripts load `API_KEY` from their adjacent `.env`. Do not read that file,
load `~/.zshrc`, print credentials, or substitute normal-connection review calls.
The PAT account must differ from the PR author. Never publish separate inline
comments, top-level PR comments, or an additional approval summary.

After a failed or uncertain response, check existing reviews before retrying and
recheck the head to avoid duplicates or reviewing an unaudited commit. Report
publication failures and unpublished findings in chat; do not change the verdict
to make publication succeed.

Report both verdicts and the combined verdict in chat, with the reviewed range,
rationale, confidence, checks, limits and global feedback. After either script
succeeds, include its returned reviewer, commit, state and review link.
