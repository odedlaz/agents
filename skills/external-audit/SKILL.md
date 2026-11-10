---
name: external-audit
description: Run adversarial PR audits when the user asks to external-audit a PR or invokes /external-audit. Use one reviewer for initial screening and correction diffs, then parallel final full reviews with early rejection before PAT-backed approval. Publish deduplicated inline change requests when needed.
---

# External Audit

An invocation authorizes the complete automatic audit loop: screening, correction diffs, shallow retries, range correction, final-full reviews after shallow acceptance, and formal GitHub reviews through the private scripts. Continue these stages without asking the user for permission, a readiness decision, or a separate full-audit request. An explicit user pause or stage limit overrides this authorization. Findings belong inside reviews, not standalone comments. Keep verdict explanations and global feedback in chat. Do not merge or authorize code changes through this skill alone. Resolve the PR URL from the request or unambiguous context; ask if the target is ambiguous.

## Reviewer configuration

Change reviewer models and settings only in this table. Use the role and profile names everywhere else.

| Profile | Role | Provider | Model | Reasoning effort | Mode |
| --- | --- | --- | --- | --- | --- |
| `openai-deep` | `openai` | Codex | `gpt-6.1-sol` | high | regular |
| `anthropic-deep` | `anthropic` | Anthropic | `claude-opus-5-5` | high | regular |
| `openai-shallow` | `openai` | Codex | `gpt-6.1-sol` | low | regular |

Use `openai-shallow` alone for `initial-full` screening and correction `diff` reviews. Start both deep profiles in parallel for `final-full` only after a complete shallow review accepts the current head and verifies all open required findings. Failure, incomplete coverage, repeated retries, and base changes never bypass this gate. Review range and profile are separate: initial screening still covers the entire PR. Use the shallow profile for finding re-checks before this gate; a deep re-check also requires shallow acceptance. All profiles retain the same finding and evidence standards.

Resolve the exact provider IDs and supported options from runtime capabilities. Set the configured model, effort and mode explicitly; do not inherit settings that can enable fast mode. If a required configuration is unavailable, report the limitation; do not substitute another model.

In T3 Code, use `orchestrator_capabilities` before the first `delegate_task`, pass settings in `target.options`, and follow returned continuation instructions. Use supported delegation tools in other runtimes. Start a fresh agent for every review or re-check, without inherited conversation or implementation context. Reviewers never implement fixes or publish to GitHub.

## Track each reviewer separately

Keep a per-PR record for each role: last completed review SHA, last accepted SHA, profile, mode and range, coverage status, unresolved findings, and publication results. History belongs to the provider role, not the profile: switching profiles preserves its cursor and findings. Track shallow acceptance separately from deep-role results, with its screened range and current PR base and head; a base or head change invalidates this gate. Track a final-full cycle ID and its results separately. Recover this record from prior chat audit records and submitted reviews before starting. Match older role labels by their recorded provider or model so a rename does not reset history. Record results even when publication failed. Only a review with complete coverage advances the completed-review SHA, including a completed rejection. Early rejections, cancellations, failed and interrupted runs do not advance it; keep their confirmed findings open.

Outside the final-full stage, a repeat request uses a diff audit even if the user says only "audit this PR" or invokes `/xaudit` or `/external-audit` again:

- `first-range` The first screening review uses `openai-shallow`, mode `initial-full`, and the real PR base to current head. For a stacked PR, use that layer's base. The `anthropic` role starts at the full-review stage and always receives the entire PR range.
- `repeat-range` Except for the verified base change below, correction reviews use `openai-shallow`, mode `diff`, and the `openai` role's own last completed review SHA to current head. Never use the other role's cursor or reset to the PR base.
- `base-changed` When a verified upstream merge or rebase changes the PR base and adds upstream changes to the correction range, automatically use `openai-shallow`, mode `diff`, over the actual current PR base to head. Record why the range changed and retain the previous completed-review cursor until this review completes. Retry this corrected range with shallow reviewers; no permission question or deep escalation.
- `full-range` An explicit full-audit request resets the shallow screening range to the actual PR base and head, using mode `initial-full`. It overrides the repeat-range default but still requires shallow acceptance before final-full.
- `final-range` The final approval stage always uses the real PR base to current head for both roles, with mode `final-full`. For a stacked PR, use that layer's base. It is a new review of the whole PR, including unchanged code and interactions between corrections.

For a repeat diff, recover the previous `openai` SHA or ask for it. Fetch unavailable commits; do not invent a replacement SHA or silently reset an ordinary correction diff. The verified base-change rule above authorizes range correction without changing the reviewer profile. Compare the supplied commits directly. Reuse complete results only for the same range and stage, and final-full results only within the same cycle. A finding re-check can use its prior range and closure checklist at the same head; an empty diff is not proof of correction. Publication failure does not erase completed review coverage.

Supply only [the auditor prompt](references/auditor-prompt.md) unchanged, repository location, PR URL, role, profile, audit mode and both SHAs. Include a minimal checklist of all still-open required findings and closure conditions, including findings from either full reviewer, so earlier defects cannot disappear outside a new diff. Do not supply old review prose, conversation history, implementation claims or author-proposed solutions. The reviewer must verify the checklist against code and tests independently. Finding closure during screening does not replace final-full acceptance.

- `stable-prefix` Put the unchanged auditor prompt first in every delegation, then append the role, profile, repository, PR, mode, SHAs and finding checklist in a consistent order. Keep tool definitions and configured model settings stable within each profile where the runtime permits. This can support prefix-cache reuse without inherited conversation. Cache controls belong to the runtime; do not invent options, resume old reviewers or add unrelated context to obtain a cache hit.

## Run the automatic review loop

- `screen-round` Start one fresh `openai-shallow` reviewer for initial screening or a correction diff. Publish required findings, make corrections only when authorized, and repeat shallow diff reviews until it accepts the current head with no unresolved required findings. Do not start an `anthropic` screening or diff reviewer.
- `parallel-full` Only after the shallow gate passes, start fresh `openai-deep` and `anthropic-deep` reviewers together for full reviews. Neither role waits for the other's acceptance before starting. Process results as they arrive; do not wait for both before checking for rejection. Reuse completed results only for the same range and stage.
- `retry-shallow` If an initial screening or correction diff fails or returns incomplete coverage without a confirmed required finding, keep retrying with fresh `openai-shallow` reviewers at the same valid range. Preserve cursors and open findings; incomplete work is not acceptance. Never switch to deep models or ask the user to permit a full audit as recovery. A concrete runtime or model-access blocker must be reported and resolved before retrying; it does not authorize bypassing shallow acceptance.
- `final-full` After complete shallow screening or diff acceptance, start a new final-full cycle over the entire PR with both deep reviewers in parallel. No separate readiness command is required. An explicit full-audit request follows the same shallow gate and then this final-full stage. It is mandatory even when initial screening passes immediately at the unchanged head. A required finding rejects the cycle: publish it, return to corrections and single-reviewer diffs, then start a new final-full cycle after screening accepts again.
- `reject-early` In final-full mode, a reviewer may return immediately after confirming an actionable required finding with enough evidence to publish it. Suspicions and optional feedback do not trigger early rejection. As soon as that result arrives, reject the cycle and cancel its unfinished peer; do not wait for peer agreement. In T3 Code use `task_cancel` for a delegated task, not a thread interrupt. In other runtimes use supported cancellation. Preserve confirmed findings already returned by either reviewer and publish them once with semantic duplicates removed. If cancellation is unavailable, report the limitation and let the peer finish; stop or finish it before editing its checkout. Do not advance cursors from partial coverage or reuse acceptances from a rejected cycle.
- `resume-cycle` If a final-full cycle has no rejection but a reviewer fails or is interrupted, retry only the missing role at the unchanged range. A rejected cycle requires two fresh final-full reviews after corrections, even if a prior peer accepted.
- `approve-round` Run `approve` only after both final-full reviews in the same cycle complete the entire PR review and accept the current PR base and head with no unresolved required findings. Recheck the range before publication and approval. Any new commit or changed final-review base invalidates final-full acceptance; a new base or head needs fresh shallow acceptance followed by fresh final-full reviews. A failed or unavailable peer blocks approval, but does not block publication of valid required findings.

The parent may implement corrections only when the user has authorized that work. If fixes are authorized, continue the loop until both final-full reviews accept. Otherwise, report the findings after publication and resume single-reviewer diffs when a later request supplies fixes. Do not make edits or merges merely to finish an audit.

- `independent-verdicts` Each role returns its own verdict without waiting for peer agreement or starting routine peer debate. Either role can require a correction; approval consensus means both final-full reviews accept the final commit. The parent combines duplicate findings for publication.

Keep prior findings open until their corrections are explicitly verified, including findings outside the current diff. Missing evidence, failed reviews, ambiguous verdicts and publication failures cannot count as acceptance. If the parent disputes a finding, keep it open and obtain a fresh re-check instead of discarding it or forcing agreement.

## Publish and report

Only the parent runs the private scripts. Resolve `approve` and `request-changes` beside this `SKILL.md` and use their absolute paths.

For a round with `REQUEST CHANGES`, submit one formal review containing the required findings from either role. Merge reports of the same underlying defect, even when wording, slugs or nearby anchors differ. Keep distinct defects separate, including those on the same line. Assign one stable slug and one inline comment per defect. Do not repost an unchanged finding already present in an open review; report its existing link and keep it open.

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

- `compact-results` After each review, give one compact chat result with the role, profile, mode, final-full cycle ID when applicable, both SHAs, coverage status, verdict, short rationale, confidence, checks, limits and open-finding status. Mark early rejections and cancelled peers as incomplete; do not describe them as complete full reviews. Put each finding's evidence, impact and correction in its review comment once; do not repeat full findings or investigation narratives in the summary. Keep enough evidence to assess the verdict.

Distinguish a recommended verdict from a submitted GitHub review. Complete required publication before reporting that round as complete; include the script's reviewer, commit, state and review link. If submission did not occur, state the concrete blocker. After final approval, report both roles' final-full range and the approval link. If that approval was already published for the current head, report the existing link instead of calling the script again.
