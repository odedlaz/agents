---
name: external-audit
description: Run adversarial PR audits when the user asks to external-audit a PR or invokes /external-audit. Prepare with screening diffs, run one full-PR review, then finish with correction diffs. Publish deduplicated inline change requests or PAT-backed approval.
---

# External Audit

An invocation authorizes preparation diffs, one full review, correction diffs, incomplete-review retries, range recovery and formal GitHub reviews through the private scripts. Continue without asking for permission or a readiness decision. Explicit user pauses or limits override this authorization. Findings belong inside reviews, not standalone comments; keep verdict explanations and global feedback in chat. This skill does not authorize code edits or merges. Resolve the PR from the request or unambiguous context; ask if the target is ambiguous.

## Reviewer configuration

Change models and settings only in this table. Use profile and role names elsewhere.

| Profile | Role | Provider | Model | Reasoning effort | Mode |
| --- | --- | --- | --- | --- | --- |
| `openai-deep` | `openai` | Codex | `gpt-6.1-sol` | high | regular |
| `anthropic-deep` | `anthropic` | Anthropic | `claude-opus-5-5` | high | regular |
| `openai-shallow` | `openai` | Codex | `gpt-6.1-sol` | low | regular |
| `anthropic-shallow` | `anthropic` | Anthropic | `claude-opus-5-5` | low | regular |

Use `openai-shallow` for preparation diffs. After complete acceptance, run `anthropic-deep` once over the full current PR. After that full review completes, use only `openai-deep` for correction diffs and finding closure until approval. Do not launch an OpenAI full review, return to preparation or repeat the completed Anthropic full review after findings or new commits. `anthropic-shallow` is inactive and retained for future configuration. All active profiles apply the same finding and evidence standards.

Resolve provider IDs and supported options from runtime capabilities. Set configured model, effort and regular mode explicitly; do not inherit fast mode. If a configuration is unavailable, report the blocker without substituting a model. In T3 Code, call `orchestrator_capabilities` before the first `delegate_task`, pass settings in `target.options` and follow continuation instructions. Use supported delegation tools elsewhere. Every review or re-check starts a fresh agent without inherited conversation, implementation context or the other reviewer's verdict. Reviewers do not fix code or publish to GitHub.

## Track phase and review history

Keep a per-PR phase: `preparation`, `full-review`, `corrections` or `approved`. Record the preparation cursor, correction cursor and its source, current PR base/head, configured settings, audit modes, coverage, findings and publication results. The full-review checkpoint records the complete `anthropic-deep` result at its pinned PR base/head, even on rejection. Recover this checkpoint and phase across requests and sessions from chat audit records and submitted reviews; a recurring invocation does not start a new cycle.

Only complete reviews advance cursors, even on rejection or failed publication. Preparation owns its completed diff-review cursor. After the Anthropic full review completes at H, set the correction range baseline to H; this is the full-reviewed snapshot, not a claim that OpenAI reviewed H. Subsequent complete `openai-deep` correction diffs advance that cursor. Do not advance the preparation cursor from full or correction reviews. Partial, cancelled, failed and interrupted work never advances cursors or completes the checkpoint. Preserve confirmed findings from incomplete work.

Match history by actual provider/model/effort/runtime mode, audit mode and coverage, not profile name alone. Reuse results only when settings, range, reviewed code and finding-closure evidence still match. Preserve findings from every prior configuration. A previous dual-review cycle's complete matching Anthropic full result can establish this checkpoint; the old OpenAI full result is not required. Do not repeat a valid Anthropic full review only because this workflow changed. Missing checkpoint data must be recovered, not invented or silently reset.

A new head or PR base invalidates current acceptance but preserves a completed full-review checkpoint. Full review covers a pinned snapshot; later changes stay in correction diffs. Only an explicit user request for another full review starts another cycle. An ordinary re-review or rescan does not reset the phase.

## Select review ranges

- `preparation-range` With no matching preparation history, use actual PR base to current head, mode `diff`; stacked PRs use that layer's base. Otherwise use the last completed preparation SHA to current head, plus every open-finding check.
- `full-range` Only `anthropic-deep` runs mode `final-full`, over actual PR base and head pinned at launch, including retries if the live PR moves. Review the entire PR and interactions across changes, not only prior findings or preparation evidence. Do not apply fixes before this review completes.
- `correction-range` After the full review completes at H, review H..next-head with `openai-deep`, mode `diff`, plus every open-finding check from Anthropic and earlier configurations. Advance the correction cursor after each complete correction review. Rejection never triggers another full review. An unchanged-head finding re-check can reuse its prior range and closure checklist; an empty diff does not prove correction.
- `base-changed` After a verified upstream merge or rebase introduces upstream changes or invalidates a diff cursor, automatically review actual current PR base-to-head in the current diff phase. This recovered range overrides the ordinary cursor-to-head range. Before full-review launch, preparation must accept the recovered range. An already-running full review finishes its pinned snapshot, then correction diffs cover new work. After the checkpoint, keep correction mode and the checkpoint. Recovery needs no readiness or permission question.
- `explicit-rescan` A request to rescan all PR changes sets the current diff phase's next range to actual base-to-head. It does not repeat a completed full review unless the user explicitly requests another.

Fetch unavailable commits. Recover a missing diff cursor from history or ask for it; do not invent a SHA or silently reset an ordinary correction range. Read relevant surrounding code and tests during diffs without reopening unrelated unchanged code as a new audit scope.

Supply only [the auditor prompt](references/auditor-prompt.md) unchanged, repository, PR URL, role, profile, audit mode and both range SHAs. Add current PR base and a minimal checklist of all open required findings and closure conditions, including the other provider's and retired configurations' findings. Do not send old review prose, author-proposed solutions, conversation, implementation claims or peer verdicts. Each fresh reviewer verifies findings independently; earlier defects cannot disappear because they lie outside the current diff.

- `stable-prefix` Put the unchanged prompt first, then role, profile, repository, PR, mode, range SHAs, current PR base and checklist in that order. Keep supported system instructions, tool definitions and tool order stable. Cache reuse must not inherit conversation or conclusions. Read [runtime cost controls](references/cost-controls.md) when configuring cache, tools or context; use only supported controls without changing reviewer settings.

## Run the automatic review loop

- `reuse-approval` Reuse a published approval only when current base/head, settings, required phase coverage and findings still match. Recover the existing phase before starting outstanding work. A stale approval does not reset the full-review checkpoint.
- `prepare-round` In `preparation`, run fresh `openai-shallow` diffs until complete acceptance with no open required findings. Publish findings, fix code only when authorized, then repeat preparation diffs. A rejection does not start full review.
- `full-round` After preparation accepts, recheck base/head and launch fresh `anthropic-deep` over the full range. This transition is automatic. Collect complete coverage and all findings, then record the checkpoint regardless of verdict. If it finds issues, publish them and move to `corrections`, never back to preparation. Complete acceptance at unchanged base/head with no open findings permits approval directly. No OpenAI full review runs.
- `correct-round` In `corrections`, apply authorized fixes and run fresh `openai-deep` diffs. Verify all open findings, including Anthropic findings outside the delta, and report new defects. Rejections repeat only correction diffs after fixes. Complete acceptance through the current head with no open findings permits approval. Do not launch Anthropic again, preparation or any full review. New commits after an accepted full review also use this phase.
- `incomplete-round` Preserve findings and retry the incomplete profile over its unchanged assigned range with a fresh reviewer. Partial publication does not advance cursors, permit corrections or complete a phase. If the live PR base/head changes during full review, complete/retry its pinned snapshot, record the checkpoint, then cover new work with correction diffs. Fetch missing pinned commits or report a blocker rather than substituting another range. After a completed checkpoint, retries and recovery stay in correction diffs. Resolve concrete access/runtime blockers; no retry count bypasses complete coverage.
- `approve-round` Approval requires the completed Anthropic full-review checkpoint. Its complete acceptance at unchanged base/head with no findings permits approval directly. If it rejected or code/base changed afterward, require complete accepting `openai-deep` correction coverage through the current head with every required finding independently verified closed. No new Anthropic acceptance at the corrected head is required. Recheck base/head and publication state immediately before `approve`.

Do not stop a reviewer at the first defect. Fix code only when authorized; otherwise report published findings and resume in the saved phase when fixes arrive. Missing evidence, ambiguous verdicts or publication failures cannot count as acceptance. Disputed findings need a fresh re-check, not forced agreement or silent dismissal. Do not merge just to finish an audit.

## Publish and report

Only the parent runs the private scripts. Resolve `approve` and `request-changes` beside this `SKILL.md` and use their absolute paths.

For required findings from a complete rejection or partial report, submit one formal review containing required findings verified by the reviewing profile, including carried findings still open from earlier reviews. Merge reports of the same underlying defect, even when wording, slugs or nearby anchors differ. Keep distinct defects separate, including those on the same line. Assign one stable slug and one inline comment per defect. Do not repost an unchanged finding already present in an open review; report its existing link and keep it open. Publication of partial findings does not complete that review round.

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

If the live head moves during full review, record completed pinned coverage and its checkpoint separately from publication. Preserve unpublished findings, then verify and reanchor them at the current head during correction coverage before submitting required findings. Do not submit a stale reviewed head or report unpublished findings as submitted. Publication failure does not prevent the correction review needed to recover current-head coverage.

After a failed or uncertain response, check existing reviews before retrying and recheck the head to avoid duplicates or reviewing an unaudited commit. Report publication failures and unpublished findings in chat; do not change the verdict to make publication succeed.

- `compact-results` After each review, give one compact chat result with the role, profile, mode, both SHAs, coverage status, verdict, short rationale, confidence, checks, limits and open-finding status. Mark partial, failed, interrupted or cancelled reviews as incomplete; do not describe them as complete diff reviews. Put each finding's evidence, impact and correction in its review comment once; do not repeat full findings or investigation narratives in the summary. Keep enough evidence to assess the verdict.

Distinguish a recommended verdict from a submitted GitHub review. Report coverage completion separately from publication completion. Complete required publication before reporting the review as submitted; include the script's reviewer, commit, state and review link. If submission did not occur, state the concrete blocker. When full review completes, emit a compact checkpoint in chat with PR, phase, pinned base/head, the full profile and actual settings, coverage/verdict, open finding slugs and correction cursor. Update the saved phase and cursor in later correction results. Do not post this record as a GitHub comment. After approval, report the full-review checkpoint and latest accepting diff range, if any, and the approval link. If that approval was already published for the current head, report the existing link instead of calling the script again.
