---
name: external-audit
description: Run adversarial PR audits when the user asks to external-audit a PR or invokes /external-audit. Use one reviewer for screening and correction diffs, then a fresh full-PR reviewer after acceptance before PAT-backed approval. Publish deduplicated inline change requests when needed.
---

# External Audit

An invocation authorizes the complete automatic audit loop: screening, correction diffs, incomplete-review retries, range correction, final-full review after screening acceptance, and formal GitHub reviews through the private scripts. Continue without asking for permission, a readiness decision or a separate full-audit request. An explicit user pause or stage limit overrides this authorization. Findings belong inside reviews, not standalone comments. Keep verdict explanations and global feedback in chat. Do not merge or authorize code changes through this skill alone. Resolve the PR URL from the request or unambiguous context; ask if the target is ambiguous.

## Reviewer configuration

Change models and settings only in this table. Use profile names elsewhere.

| Profile | Role | Provider | Model | Reasoning effort | Mode |
| --- | --- | --- | --- | --- | --- |
| `openai-deep` | `openai` | Codex | `gpt-6.1-sol` | xhigh | regular |
| `anthropic-deep` | `anthropic` | Anthropic | `claude-opus-5-5` | high | regular |
| `openai-shallow` | `openai` | Codex | `gpt-6.1-sol` | high | regular |
| `anthropic-shallow` | `anthropic` | Anthropic | `claude-opus-5-5` | high | regular |

The active workflow uses only `openai-shallow` for `initial-full` screening, correction `diff` reviews and finding re-checks, then one fresh `anthropic-deep` reviewer for `final-full`. The `openai-deep` and `anthropic-shallow` rows are retained for future configuration and must not run or be required for approval. Profile labels identify workflow stages. Initial screening still covers the entire PR. Start final-full only after complete screening acceptance of the current base and head with all open required findings verified. Failure, incomplete coverage, repeated retries and base changes never bypass this gate. All profiles retain the same finding and evidence standards.

Resolve provider IDs and supported options from runtime capabilities. Set the configured model, effort and regular mode explicitly; do not inherit fast mode. If a required configuration is unavailable, report the limitation without substituting a model.

In T3 Code, use `orchestrator_capabilities` before the first `delegate_task`, pass settings in `target.options`, and follow continuation instructions. Use supported delegation tools elsewhere. Every review or re-check starts a fresh agent without inherited conversation, implementation context or prior reviewer conclusions. Reviewers never implement fixes or publish to GitHub.

## Track stages and review history

Keep a per-PR record of completed review SHAs, accepted SHAs, provider, profile, model, effort, runtime mode, audit mode, range, coverage, open findings and publication results. Track screening acceptance and its current PR base/head separately from the final-full cycle and result. A changed base or head invalidates both gates. Reuse acceptances only when stage, range, model, effort and runtime mode match the active workflow; old dual-review approvals do not automatically satisfy the new stage records. Preserve all unresolved findings from older providers and configurations.

Keep a screening/diff cursor separate from final-full results. On migration from an earlier workflow, recover the last completed screening or correction SHA, including an earlier provider's cursor. If legacy history has no separate screening stage, seed this cursor from its last completed review and record the source. Changing providers must not silently reset an ordinary diff to the PR base. Record its source. Recover state from chat audit records and submitted reviews before starting, and keep results even if publication failed. Only complete coverage advances a completed-review cursor, including a complete rejection. Partial, cancelled, failed or interrupted work cannot advance it; keep its confirmed findings open.

A repeat request uses a diff audit even if the user says only "audit this PR" or invokes `/xaudit` or `/external-audit` again:

- `first-range` With no prior review history, use `openai-shallow`, mode `initial-full`, over the actual PR base to current head. For a stacked PR, use that layer's base.
- `repeat-range` Use `openai-shallow`, mode `diff`, from the recovered last completed screening/correction SHA to current head. Do not use a stale final-review cursor or reset to the PR base.
- `base-changed` After a verified upstream merge or rebase changes the base and adds upstream changes to the correction range, automatically use `openai-shallow`, mode `diff`, over the actual current PR base to head. Record why the range changed; retain the old cursor until this review completes. Retry the corrected range at the screening stage without a permission question or final-stage escalation.
- `full-range` An explicit full-audit request resets screening to the actual PR base and head, mode `initial-full`. It overrides the repeat default but still needs screening acceptance before final-full.
- `final-range` The final reviewer always gets the entire real PR base-to-head range, including unchanged code and interactions between corrections. For a stacked PR, use that layer's base.

Recover a missing correction cursor or ask for it; fetch unavailable commits. Do not invent SHAs or silently replace an ordinary correction range. Compare supplied commits directly. Reuse complete results only for the same range and stage, and final-full results only within the same cycle. A targeted re-check can reuse its prior range and closure checklist at the same head; an empty diff does not prove correction.

Supply only [the auditor prompt](references/auditor-prompt.md) unchanged, repository, PR URL, role, profile, audit mode and both SHAs. Add a minimal checklist of all open required findings and closure conditions, including older providers' findings. Do not send old review prose, conversation, author-proposed solutions, implementation claims or the screening verdict to the final reviewer. Each fresh reviewer verifies code and tests independently. Screening acceptance never replaces final-full acceptance, even when both stages use the same model and effort.

- `stable-prefix` Put the unchanged auditor prompt first, then append role, profile, repository, PR, mode, SHAs and finding checklist in that order. Keep supported system instructions, tool definitions and tool order stable. Cache reuse must not inherit conversation or conclusions. Read [runtime cost controls](references/cost-controls.md) when configuring caching, tool loading or context management; use only supported controls without changing configured settings.

## Run the automatic review loop

- `unchanged-approved` Before launching, verify any existing published approval against the current base/head, active settings, complete screening acceptance, complete final-full acceptance and no open required findings. If all match, report it without another cycle. An explicit full audit still reruns both stages. Missing records, changed code/settings or unresolved findings prevent reuse. Preserve independently valid screening acceptance if only the final profile changed.
- `screen-round` Start one fresh `openai-shallow` reviewer for initial screening or a correction diff. After complete rejection, publish required findings, make corrections only when authorized, and repeat correction diffs until the current base/head is accepted with all open findings verified.
- `retry-screening` Incomplete or failed screening must retry with fresh `openai-shallow` reviewers over the same valid range. Preserve cursors and findings. No retry count permits skipping the screening gate or asking for permission to escalate. Report and resolve concrete runtime or model-access blockers before retrying.
- `final-full` After complete screening acceptance, recheck the base/head and start one fresh `anthropic-deep` reviewer in a new cycle over the entire PR. No separate readiness command is needed. This stage is mandatory even when initial screening passes immediately at an unchanged head, except for verified reuse under `unchanged-approved`.
- `complete-round` Every reviewer must finish the assigned scope and collect all confirmed required findings before a normal verdict. Do not stop at the first defect or start corrections while review is incomplete. A complete final rejection rejects the cycle: publish deduplicated findings, return to authorized corrections and screening diffs, then require a fresh final-full review after screening accepts again.
- `resume-cycle` Preserve confirmed findings from failed or interrupted work and retry that stage with a fresh reviewer over the unchanged range, even when a defect was found. Partial findings can be published, but partial coverage cannot advance cursors, permit corrections or start the next stage. A failed final review can retry at the same range while screening acceptance remains valid; a rejected cycle needs a fresh final review after corrections pass screening.
- `approve-round` Run `approve` only after complete screening acceptance and a complete accepting final-full review of the same current base/head, with no open required findings. Recheck the range before publication and approval. New commits or a changed base need fresh screening acceptance and then fresh final-full acceptance. A failed or unavailable reviewer blocks approval, but not publication of valid findings.

Only implement corrections when the user authorized fixes. If authorized, continue until the final review accepts; otherwise report published findings and resume diffs when fixes arrive. Do not edit or merge just to finish an audit. Keep findings open until corrections are verified, including findings outside the diff. Missing evidence, ambiguous verdicts and publication failures cannot count as acceptance. Disputed findings require a fresh re-check, not forced agreement or silent dismissal.

## Publish and report

Only the parent runs the private scripts. Resolve `approve` and `request-changes` beside this `SKILL.md` and use their absolute paths.

For a round with `REQUEST CHANGES`, submit one formal review containing the required findings from the reviewer. Merge reports of the same underlying defect, even when wording, slugs or nearby anchors differ. Keep distinct defects separate, including those on the same line. Assign one stable slug and one inline comment per defect. Do not repost an unchanged finding already present in an open review; report its existing link and keep it open.

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

- `compact-results` After each review, give one compact chat result with the role, profile, mode, final-full cycle ID when applicable, both SHAs, coverage status, verdict, short rationale, confidence, checks, limits and open-finding status. Mark partial, failed, interrupted or cancelled reviews as incomplete; do not describe them as complete full reviews. Put each finding's evidence, impact and correction in its review comment once; do not repeat full findings or investigation narratives in the summary. Keep enough evidence to assess the verdict.

Distinguish a recommended verdict from a submitted GitHub review. Complete required publication before reporting that round as complete; include the script's reviewer, commit, state and review link. If submission did not occur, state the concrete blocker. After final approval, report the screening and final-full profiles and ranges, and the approval link. If that approval was already published for the current head, report the existing link instead of calling the script again.
