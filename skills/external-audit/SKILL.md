---
name: external-audit
description: Run adversarial PR audits when the user asks to external-audit a PR or invokes /external-audit. Prepare with screening diffs, run one parallel full-PR review pair, then finish with correction diffs. Publish deduplicated inline change requests or PAT-backed approval.
---

# External Audit

An invocation authorizes preparation diffs, one full-review pair, correction diffs, incomplete-review retries, range recovery and formal GitHub reviews through the private scripts. Continue without asking for permission or a readiness decision. Explicit user pauses or limits override this authorization. Findings belong inside reviews, not standalone comments; keep verdict explanations and global feedback in chat. This skill does not authorize code edits or merges. Resolve the PR from the request or unambiguous context; ask if the target is ambiguous.

## Reviewer configuration

Change models and settings only in this table. Use profile and role names elsewhere.

| Profile | Role | Provider | Model | Reasoning effort | Mode |
| --- | --- | --- | --- | --- | --- |
| `openai-deep` | `openai` | Codex | `gpt-6.1-sol` | high | regular |
| `anthropic-deep` | `anthropic` | Anthropic | `claude-opus-5-5` | high | regular |
| `openai-shallow` | `openai` | Codex | `gpt-6.1-sol` | low | regular |
| `anthropic-shallow` | `anthropic` | Anthropic | `claude-opus-5-5` | low | regular |

Use `openai-shallow` for preparation diffs. After complete acceptance, run `openai-deep` and `anthropic-deep` once in parallel over the full current PR. After that pair completes, use only `openai-deep` for correction diffs and finding closure until approval. Do not return to preparation or repeat the completed full pair after findings or new commits. `anthropic-shallow` is inactive and retained for future configuration. All active profiles apply the same finding and evidence standards.

Resolve provider IDs and supported options from runtime capabilities. Set configured model, effort and regular mode explicitly; do not inherit fast mode. If a configuration is unavailable, report the blocker without substituting a model. In T3 Code, call `orchestrator_capabilities` before the first `delegate_task`, pass settings in `target.options` and follow continuation instructions. Use supported delegation tools elsewhere. Every review or re-check starts a fresh agent without inherited conversation, implementation context or the other reviewer's verdict. Reviewers do not fix code or publish to GitHub.

## Track phase and review history

Keep a per-PR phase: `preparation`, `full-pair`, `corrections` or `approved`. Record the preparation cursor, correction cursor, current PR base/head, configured settings, audit modes, coverage, findings and publication results. The full-pair checkpoint records both reviewers' complete results at the same pinned PR base/head, even when one or both reject. Recover this checkpoint and phase across audit requests and sessions from chat audit records and submitted reviews; a recurring invocation does not start a new cycle.

Only complete reviews advance cursors, even on rejection or failed publication. Preparation owns its completed diff-review cursor. Seed the correction cursor from `openai-deep`'s completed full-review head, then advance it with complete correction diffs. Do not copy the Anthropic cursor or advance the preparation cursor from full reviews. Partial, cancelled, failed and interrupted reviews never advance cursors or complete the full-pair checkpoint. Preserve confirmed findings from incomplete work.

Match history by actual provider/model/effort/runtime mode, audit mode and coverage, not profile name alone. Reuse complete results only when settings, range, reviewed code and finding-closure evidence still match. Preserve all findings from older configurations. An old single full review or a different effort level cannot establish the dual full-pair checkpoint. Missing checkpoint data must be recovered, not invented or silently reset.

A new head or PR base invalidates current acceptance, but does not erase a completed full-pair checkpoint. The full pair reviews a pinned snapshot; later changes require correction coverage, not a replacement pair. After that checkpoint, new work stays in correction diffs. Restart a full cycle only when the user explicitly requests another full review; an ordinary re-review or rescan does not reset the phase.

## Select review ranges

- `preparation-range` With no matching preparation history, use actual PR base to current head, mode `diff`; stacked PRs use that layer's base. Otherwise use the last completed preparation SHA to current head, plus every open-finding check.
- `full-range` Both full reviewers and any retries use the actual PR base and head pinned when the pair launches, mode `final-full`, even if the live PR moves later. Independently review the entire PR and interactions across changes. Do not narrow to preparation evidence, prior findings or the latest correction. Keep code unchanged while the pair runs; do not apply fixes before both complete.
- `correction-range` After the pair completes at head H, review H..next-head with `openai-deep`, mode `diff`, plus all open-finding checks from either provider and earlier configurations. After each complete correction review, advance only this cursor. Rejection does not trigger another full pair. An unchanged-head finding re-check can reuse its prior range and closure checklist; an empty diff does not prove correction.
- `base-changed` After a verified upstream merge or rebase adds upstream changes or invalidates a diff cursor, automatically review actual current PR base-to-head in the current diff phase. Before the pair launches, preparation must accept the recovered range. An already-running pair finishes its pinned snapshot before correction recovery. After the checkpoint, use correction diffs and keep the checkpoint. Range recovery needs no readiness or permission question.
- `explicit-rescan` A request to rescan all PR changes sets the current diff phase's next range to actual base-to-head. It does not repeat a completed full pair unless the user explicitly requests another full review.

Fetch unavailable commits. Recover a missing diff cursor from history or ask for it; do not invent a SHA or silently reset an ordinary correction range. Read relevant surrounding code and tests during diffs without reopening unrelated unchanged code as a new audit scope.

Supply only [the auditor prompt](references/auditor-prompt.md) unchanged, repository, PR URL, role, profile, audit mode and both range SHAs. Add current PR base and a minimal checklist of all open required findings and closure conditions, including the other provider's and retired configurations' findings. Do not send old review prose, author-proposed solutions, conversation, implementation claims or peer verdicts. Each fresh reviewer verifies findings independently; earlier defects cannot disappear because they lie outside the current diff.

- `stable-prefix` Put the unchanged prompt first, then role, profile, repository, PR, mode, range SHAs, current PR base and checklist in that order. Keep supported system instructions, tool definitions and tool order stable. Cache reuse must not inherit conversation or conclusions. Read [runtime cost controls](references/cost-controls.md) when configuring cache, tools or context; use only supported controls without changing reviewer settings.

## Run the automatic review loop

- `reuse-approval` Reuse a published approval only when current base/head, configured settings, required phase coverage and finding records still match. Recover the existing phase before starting outstanding work. A stale approval does not reset the completed full-pair checkpoint.
- `prepare-round` In `preparation`, run fresh `openai-shallow` diffs until one completely accepts with no unresolved required findings. Publish confirmed findings, apply fixes only when authorized, then repeat preparation diffs. A rejection does not start full reviewers.
- `full-pair-round` After preparation accepts, recheck base/head and launch fresh `openai-deep` and `anthropic-deep` in parallel over the full range. The transition is automatic. Both finish their assigned scope and return independent verdicts; do not stop or cancel a peer because the other finds a defect. Collect both complete results, deduplicate required findings and record the checkpoint regardless of acceptance or rejection. If either finds issues, publish them and move to `corrections`, never back to preparation. If both accept at the unchanged base/head with no open findings, approve directly.
- `correct-round` In `corrections`, apply authorized fixes and run fresh `openai-deep` diffs. Verify all open findings, including Anthropic findings outside the delta, and report any new defects. Rejections repeat only correction diffs after fixes. Complete acceptance through the current head with no open required findings permits approval; do not launch Anthropic, preparation or another full pair. New commits after an accepted pair also use this phase.
- `incomplete-round` Preserve findings and retry only the incomplete profile over its unchanged assigned range with a fresh reviewer. Partial publication does not advance cursors, permit corrections or complete a phase. During the full pair, reuse a complete peer result while the pinned base/head and settings still match. If the live PR base/head changes while the pair runs, finish and recover both reviews at the pinned snapshot, record that checkpoint, then review the new work with correction diffs. Do not rerun a completed peer merely because the live PR moved. Fetch missing pinned commits or report a concrete blocker rather than substituting another range. After a completed checkpoint, retries and range recovery stay in correction diffs. Resolve concrete access/runtime blockers before retrying; no retry count bypasses complete coverage.
- `approve-round` Approval requires a completed dual full-pair checkpoint. At that same base/head, both complete acceptances with no open findings permit approval. If either rejected or code/base changed afterward, require complete accepting `openai-deep` correction coverage through the current head with every required finding independently verified closed. Do not require a new Anthropic acceptance at the corrected head. Recheck current base/head and publication state immediately before `approve`.

Do not stop a reviewer at the first defect. Fix code only when authorized; otherwise report published findings and resume in the saved phase when fixes arrive. Missing evidence, ambiguous verdicts or publication failures cannot count as acceptance. Disputed findings need a fresh re-check, not forced agreement or silent dismissal. Do not merge just to finish an audit.

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

If the live head moves during the full pair, record completed pinned coverage and its checkpoint separately from publication. Preserve unpublished findings, then verify and reanchor them at the current head during correction coverage before submitting required findings. Do not submit a stale reviewed head or report unpublished findings as submitted. Publication failure does not prevent the correction review needed to recover current-head coverage.

After a failed or uncertain response, check existing reviews before retrying and recheck the head to avoid duplicates or reviewing an unaudited commit. Report publication failures and unpublished findings in chat; do not change the verdict to make publication succeed.

- `compact-results` After each review, give one compact chat result with the role, profile, mode, both SHAs, coverage status, verdict, short rationale, confidence, checks, limits and open-finding status. Mark partial, failed, interrupted or cancelled reviews as incomplete; do not describe them as complete diff reviews. Put each finding's evidence, impact and correction in its review comment once; do not repeat full findings or investigation narratives in the summary. Keep enough evidence to assess the verdict.

Distinguish a recommended verdict from a submitted GitHub review. Complete required publication before reporting that round as complete; include the script's reviewer, commit, state and review link. If submission did not occur, state the concrete blocker. When the full pair completes, emit a compact checkpoint in chat with PR, phase, pinned base/head, both profiles and actual settings, coverage/verdicts, open finding slugs and correction cursor. Update the saved phase and cursor in later correction results. Do not post this record as a GitHub comment. After approval, report the full-pair checkpoint and latest accepting diff range, if any, and the approval link. If that approval was already published for the current head, report the existing link instead of calling the script again.
