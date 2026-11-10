---
name: external-audit
description: Run adversarial PR audits when the user asks to external-audit a PR or invokes /external-audit. Screen correction diffs, then run a fresh full-PR review after screening acceptance. Publish deduplicated inline change requests or PAT-backed approval.
---

# External Audit

An invocation authorizes the automatic diff-and-full-review loop, incomplete-review retries, range recovery and formal GitHub reviews through the private scripts. Continue without asking for permission or a readiness decision. Explicit user pauses or limits override this authorization. Findings belong inside reviews, not standalone comments; keep verdict explanations and global feedback in chat. This skill does not authorize code edits or merges. Resolve the PR from the request or unambiguous context; ask if the target is ambiguous.

## Reviewer configuration

Change models and settings only in this table. Use profile and role names elsewhere.

| Profile | Role | Provider | Model | Reasoning effort | Mode |
| --- | --- | --- | --- | --- | --- |
| `openai-deep` | `openai` | Codex | `gpt-6.1-sol` | max | regular |
| `anthropic-deep` | `anthropic` | Anthropic | `claude-opus-5-5` | high | regular |
| `openai-shallow` | `openai` | Codex | `gpt-6.1-sol` | low | regular |
| `anthropic-shallow` | `anthropic` | Anthropic | `claude-opus-5-5` | low | regular |

Use only `openai-shallow` for mode `diff`, then `openai-deep` for mode `final-full` after complete screening acceptance at the current base/head. A complete rejection returns to authorized corrections and screening diffs. Do not overlap reviewers. The Anthropic rows remain for future configuration but are inactive; do not launch them or require their acceptance. Both active profiles apply the same finding and evidence standards.

Resolve provider IDs and supported options from runtime capabilities. Set configured model, effort and regular mode explicitly; do not inherit fast mode. If a configuration is unavailable, report the blocker without substituting a model. In T3 Code, call `orchestrator_capabilities` before the first `delegate_task`, pass settings in `target.options` and follow continuation instructions. Use supported delegation tools elsewhere. Every review or re-check starts a fresh agent without inherited conversation, implementation context or the other reviewer's verdict. Reviewers do not fix code or publish to GitHub.

## Track each reviewer separately

Keep per-PR, per-profile records: completed review SHA and range, last accepted SHA, current PR base, provider/model/effort/runtime mode, audit mode, coverage, open findings and publication results. Recover history from chat audit records and submitted reviews. Match records by actual settings, mode and coverage, not profile name alone. Preserve findings from retired profiles and configurations; inactive reviewers do not impose approval gates.

Only a complete `openai-shallow` diff review advances the screening cursor, even on rejection or failed publication. After a complete screening rejection of A..B and fix C, screen B..C plus all open-finding closure checks. Partial, cancelled, failed and interrupted reviews never advance it. Preserve confirmed findings from incomplete work. A deep review does not advance the screening cursor. Record deep coverage separately; its history never narrows the next full review.

Reuse complete results only when settings, audit mode, reviewed code, range and finding-closure evidence still match. A new head or changed PR base invalidates current acceptance but preserves history for range recovery. An old deep diff or a different effort level cannot satisfy the full-review gate.

## Select review ranges

- `first-range` Screening with no matching completed history uses the actual PR base to current head, mode `diff`. For stacked PRs, use that layer's base.
- `repeat-range` Screening with history uses its own last completed diff-review SHA to current head. Include all changes since that cursor and all open-finding checks, including findings from full reviews and retired configurations.
- `full-range` Every `openai-deep` review uses the entire actual PR base-to-current-head range, mode `final-full`, even after a previous full rejection. Never use its last reviewed SHA or the screening cursor as the full-review base. Review interactions across the entire PR, not only the latest correction or prior findings.
- `base-changed` After a verified upstream merge or rebase adds upstream changes or invalidates a screening cursor, automatically screen the actual current PR base-to-head diff. Retain history and findings until complete coverage replaces it. Start deep only after complete screening acceptance at the recovered base/head; recovery does not bypass screening or require a new permission question.
- `explicit-rescan` An explicit request to review all PR changes resets the next screening diff to actual base-to-head. Complete screening acceptance still precedes the full review.

Fetch unavailable commits. Recover a missing screening cursor from history or ask for it; do not invent a SHA or silently reset an ordinary repeat diff. Compare supplied commits directly. An unchanged-head finding re-check can reuse its prior range and closure checklist; an empty diff alone does not prove correction. During screening, read relevant surrounding code and tests without reopening unrelated unchanged code as a new audit scope.

Supply only [the auditor prompt](references/auditor-prompt.md) unchanged, repository, PR URL, role, profile, audit mode and both range SHAs. Add the current PR base and a minimal checklist of all open required findings and closure conditions, including retired configurations' findings. Do not send old review prose, author-proposed solutions, conversation, implementation claims or another reviewer's verdict. Each fresh reviewer verifies findings independently. Earlier defects cannot disappear because they lie outside the screening diff.

- `stable-prefix` Put the unchanged prompt first, then role, profile, repository, PR, mode, range SHAs, current PR base and checklist in that order. Keep supported system instructions, tool definitions and tool order stable. Cache reuse must not inherit conversation or conclusions. Read [runtime cost controls](references/cost-controls.md) when configuring cache, tools or context; use only supported controls without changing reviewer settings.

## Run the automatic review loop

- `reuse-approval` Before launching, verify any existing published approval against the current base/head, both active profiles' complete accepting coverage and no open findings. Deep coverage must span the full current PR. If all match, report the existing approval. Explicit rescans still rerun screening and the full review. Reuse independently valid current-head results when retrying missing work; do not reuse stale settings or coverage.
- `screen-round` Start fresh `openai-shallow` on its screening range. Finish the entire scope and all open-finding checks before a normal verdict. Complete rejection publishes deduplicated required findings and skips deep. After authorized corrections, repeat screening on its next correction diff.
- `full-round` After complete screening acceptance with no open required findings, recheck base/head and start fresh `openai-deep` over the full current PR. This transition is automatic; do not ask for readiness or permission. Complete deep rejection publishes findings and returns to authorized corrections, then screening diffs. Once screening accepts again, repeat the full deep review from actual PR base to head.
- `incomplete-round` Preserve findings and retry the same profile with a fresh reviewer over the unchanged assigned range until coverage completes. A partial report can support publication of confirmed findings, but cannot advance cursors, permit corrections or count as acceptance/rejection. Resolve concrete access/runtime blockers before retrying. A partial deep finding blocks approval but does not force screening to rerun before deep completes at unchanged base/head. If base/head changes, return to screening and recover its range. No retry count bypasses complete screening acceptance before deep.
- `approve-round` Run `approve` only after complete screening acceptance at the current base/head and complete deep acceptance of the entire current PR base-to-head range, under configured settings, with no unresolved required findings. Screening starting SHAs can differ from the full-review base. Recheck base/head immediately before publication and approval. Missing or failed reviews block approval, but not valid finding publication.

Do not stop a reviewer at the first defect. Only fix code when authorized; otherwise report published findings and resume when fixes arrive. Keep findings open until verified, including those outside the latest screening diff. Missing evidence, ambiguous verdicts or publication failures cannot count as acceptance. Disputed findings require a fresh re-check rather than forced agreement or silent dismissal. Do not merge just to finish an audit.

## Publish and report

Only the parent runs the private scripts. Resolve `approve` and `request-changes` beside this `SKILL.md` and use their absolute paths.

For required findings from a complete rejection or partial report, submit one formal review containing the required findings from either reviewer. Merge reports of the same underlying defect, even when wording, slugs or nearby anchors differ. Keep distinct defects separate, including those on the same line. Assign one stable slug and one inline comment per defect. Do not repost an unchanged finding already present in an open review; report its existing link and keep it open. Publication of partial findings does not complete that review round.

Write a JSON file with the reviewed `commit_id`, a short neutral `body`, and `comments`. Each comment needs `path`, `line`, `side` (LEFT or RIGHT), and `body` with its slug, severity, evidence, impact and required correction or proof. Preserve real newlines. Keep optional feedback and required findings without valid inline locations in chat; do not invent locations. Such required findings still block approval, and the `comments` array may be empty.

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

`request-changes` accepts `-` as the JSON path for stdin. It pins the review to `commit_id`, checks the current head, submits `REQUEST_CHANGES` with all inline comments in one review, and rejects exact duplicate comment objects. The parent removes semantic duplicates before calling it.

After `approve-round` conditions hold, run the approval script once with the PR URL as its sole argument:

```sh
EXTERNAL_AUDIT_REVIEWED_HEAD='REVIEWED_HEAD_SHA' 'APPROVE_SCRIPT_PATH' 'https://github.com/OWNER/REPO/pull/NUMBER'
```

Both scripts load `API_KEY` from their adjacent `.env`. Do not read that file, load `~/.zshrc`, print credentials, or substitute normal-connection review calls. The PAT account must differ from the PR author. Never publish separate inline comments, top-level PR comments or an additional approval summary.

After a failed or uncertain response, check existing reviews before retrying and recheck the head to avoid duplicates or reviewing an unaudited commit. Report publication failures and unpublished findings in chat; do not change the verdict to make publication succeed.

- `compact-results` After each review, give one compact chat result with the role, profile, mode, both SHAs, coverage status, verdict, short rationale, confidence, checks, limits and open-finding status. Mark partial, failed, interrupted or cancelled reviews as incomplete; do not describe them as complete diff reviews. Put each finding's evidence, impact and correction in its review comment once; do not repeat full findings or investigation narratives in the summary. Keep enough evidence to assess the verdict.

Distinguish a recommended verdict from a submitted GitHub review. Complete required publication before reporting that round as complete; include the script's reviewer, commit, state and review link. If submission did not occur, state the concrete blocker. After approval, report the screening diff and full-review ranges and the approval link. If that approval was already published for the current head, report the existing link instead of calling the script again.
