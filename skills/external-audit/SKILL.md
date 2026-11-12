---
name: external-audit
description: Run adversarial PR audits when the user asks to external-audit a PR or invokes /external-audit. Run an initial full review, contextual preparation diffs, one independent full review, then contextual correction diffs. Publish formal inline change requests or PAT-backed approval.
---

# External Audit

An invocation authorizes both one-time full stages, diff reviews, incomplete-review retries, range recovery and formal GitHub reviews through the private scripts. Continue automatically without readiness or permission questions. Explicit user pauses or limits override this authorization. Findings belong inside reviews, not standalone comments; keep verdict explanations and global feedback in chat. This skill does not authorize code edits or merges. Resolve the PR from the request or unambiguous context; ask if the target is ambiguous.

## Reviewer configuration

Change models and settings only in this table. Use profile and role names elsewhere.

| Profile | Role | Provider | Model | Reasoning effort | Mode |
| --- | --- | --- | --- | --- | --- |
| `openai-deep` | `openai` | Codex | `gpt-6.1-sol` | high | regular |
| `anthropic-deep` | `anthropic` | Anthropic | `claude-opus-5-5` | high | regular |
| `openai-shallow` | `openai` | Codex | `gpt-6.1-sol` | low | regular |
| `anthropic-shallow` | `anthropic` | Anthropic | `claude-opus-5-5` | low | regular |

Start with `openai-deep`, mode `initial-full`, without inherited context. If findings remain, use contextual `openai-shallow` preparation diffs until acceptance. Then run `anthropic-deep`, mode `final-full`, without inherited context. If findings remain afterward, use contextual `openai-shallow` correction diffs until approval. Each full stage runs once per PR, including complete rejections. A clean full verdict skips that stage's diff loop. `anthropic-shallow` is inactive and retained for future configuration.

Resolve provider IDs and supported options from runtime capabilities. Set model, effort and regular mode explicitly; do not inherit fast mode or substitute unavailable settings. Report concrete blockers. In T3 Code, call `orchestrator_capabilities` before the first `delegate_task`, pass settings in `target.options` and follow continuation instructions. Use supported delegation tools elsewhere. Every review or re-check starts a fresh agent, with context determined by audit mode below. Reviewers do not fix code or publish to GitHub.

## Track phase and coverage

Keep a per-PR phase: `initial-review`, `preparation`, `full-review`, `corrections` or `approved`. Record current base/head, each full stage's pinned range, actual profile/settings, complete or partial coverage, verdict, findings and publication state. Keep separate preparation and correction diff cursors with their sources. Recover these records across requests and sessions; an ordinary re-review does not restart full stages.

A complete initial review establishes its checkpoint even on rejection and sets the preparation baseline to its reviewed head. A complete Anthropic full review establishes its checkpoint even on rejection and sets the correction baseline to its reviewed head. These baselines do not claim earlier shallow-profile coverage. Later complete diffs advance only the current phase's cursor, even on rejection or failed publication. Partial, cancelled, failed and interrupted work advances nothing. Preserve confirmed partial findings.

Match history by actual model/settings, range, audit mode and coverage, not profile name alone. Reuse verdicts only while range, settings, relevant requirements and finding-closure evidence still match. Preserve findings from all older configurations. A matching completed OpenAI full review can establish the initial checkpoint regardless of its older stage label. A valid completed Anthropic checkpoint from an older workflow remains valid; continue corrections rather than retroactively adding an initial review. Missing checkpoint or cursor data must be recovered, not invented or silently reset.

New commits or a changed base invalidate current acceptance but preserve completed checkpoints. Restart a completed full stage only when the user explicitly requests another full review. Neither a rejection, an ordinary re-review nor a general rescan does so.

## Select ranges and context

- `full-range` Initial and Anthropic full reviews use actual PR base and head pinned at launch, mode `initial-full` or `final-full` respectively. Retries keep that snapshot even if the live PR moves. Review the entire PR and interactions across changes, not just prior findings or the latest fix. Do not apply fixes before the full review completes.
- `diff-range` Preparation starts from the initial checkpoint head; corrections start from the Anthropic checkpoint head. Later diffs use that phase's last complete diff-review SHA to current head, plus every open-finding check from any stage. An unchanged-head re-check can reuse its prior range and checklist; an empty diff alone does not prove correction.
- `base-changed` After a verified upstream merge or rebase introduces upstream changes or invalidates a diff cursor, automatically review actual current PR base-to-head in the current diff phase. This overrides the ordinary cursor range. An in-flight full review finishes its pinned snapshot first. Before Anthropic launches, new work must receive complete preparation acceptance. After its checkpoint, new work stays in correction diffs. No readiness or permission question is needed.
- `explicit-rescan` A general request to rescan all PR changes sets the current diff phase's next range to actual base-to-head without repeating completed full stages. Only an explicit request for another full review resets a checkpoint.

Fetch missing commits. Recover missing diff cursors from history or ask for them; do not invent SHAs. During diffs, read surrounding code and contracts as needed without reopening unrelated unchanged code as a new full scope.

Every reviewer receives [the auditor prompt](references/auditor-prompt.md) unchanged, repository, PR URL, role, profile, audit mode, range SHAs and current PR base.

- `diff-context` Include the user's problem or symptom, intended behavior and acceptance criteria, relevant constraints and design decisions, fix summary and rationale, prior findings with evidence and closure conditions, and relevant tests or implementation claims. Include review excerpts and task discussion that explain what the delta fixes. Use relevant inherited conversation where supported, or a focused brief otherwise; omit unrelated transcript and repeated logs. Distinguish requirements, verified facts and claims. The reviewer must verify context against code and can reject the proposed solution.
- `full-context` For both full stages and their retries, provide only the common inputs above. No inherited conversation, task/implementation narrative, prior verdict, review prose or finding checklist. Review code, tests and repository contracts independently. The parent retains historical findings; omission from a fresh full result does not close them.
- `stable-prefix` Keep the unchanged prompt first, then role, profile, repository, PR, mode, range SHAs and current PR base. Append task context and the complete open-finding checklist only in diff mode. Keep supported system instructions and tool definitions/order stable. Read [runtime cost controls](references/cost-controls.md) when configuring cache, tools or context; do not change configured reviewer settings for savings.

## Run the automatic review loop

- `reuse-approval` Reuse published approval only when current base/head, settings, phase coverage and finding records still match. A stale approval does not erase completed full checkpoints.
- `initial-round` With no initial or later full checkpoint, start fresh `openai-deep` over the full range. Complete rejection records the checkpoint, publishes findings and enters `preparation`. Complete acceptance at unchanged base/head with no historical findings permits the Anthropic stage directly; no shallow review is required first. If code/base changed or an earlier required finding remains unverified, preparation diffs must accept first.
- `prepare-round` In `preparation`, apply authorized fixes and run fresh contextual `openai-shallow` diffs. Verify all open findings, including those outside the delta. Rejections repeat only preparation diffs after fixes. Complete current-head acceptance with no open findings permits the Anthropic stage; never repeat the initial full review automatically.
- `full-round` Launch fresh `anthropic-deep` over the full range after initial or preparation acceptance at current base/head. This transition is automatic. Record complete coverage and its checkpoint regardless of verdict. If findings remain, publish them and enter `corrections`. If it completely accepts unchanged code and no historical finding remains open, approve directly. A full acceptance does not clear findings it was not given.
- `correct-round` In `corrections`, apply authorized fixes and run fresh contextual `openai-shallow` diffs. Independently verify every required finding from either provider and report new defects. Complete current-head acceptance with all findings closed permits approval. Rejections repeat only these diffs; do not rerun Anthropic or the initial full stage. New commits after Anthropic acceptance also use corrections.
- `incomplete-round` Preserve findings and retry only the incomplete profile, fresh, over its unchanged range with mode-appropriate context. Partial publication neither advances cursors nor permits corrections or completes a phase. An in-flight full review finishes/retries its pinned snapshot even if the live PR moves, then the next diff phase covers new work. Fetch missing pinned commits or report a blocker instead of substituting another range. No retry count bypasses complete coverage.
- `approve-round` Approval requires the completed Anthropic checkpoint. Its complete acceptance at unchanged base/head with no required findings permits approval directly. If it rejected or code/base changed afterward, require complete accepting correction-diff coverage through current head with every required finding verified closed. No repeated full acceptance is required. Recheck base/head and publication state immediately before `approve`.

All reviewers finish their assigned scope and collect all findings; do not stop at the first defect. Fix code only when authorized; otherwise report findings and resume in the saved phase when fixes arrive. Missing evidence, ambiguous verdicts or publication failures cannot count as acceptance. Disputed findings need an independent fresh re-check, not forced agreement or silent dismissal. Do not merge to finish an audit.

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

If the live head moves during full review, record completed pinned coverage and its checkpoint separately from publication. Preserve unpublished findings, then verify and reanchor them at the current head during the next diff phase before submitting required findings. Do not submit a stale reviewed head or report unpublished findings as submitted. Publication failure does not prevent the diff review needed to recover current-head coverage.

After a failed or uncertain response, check existing reviews before retrying and recheck the head to avoid duplicates or reviewing an unaudited commit. Report publication failures and unpublished findings in chat; do not change the verdict to make publication succeed.

- `compact-results` After each review, give one compact chat result with the role, profile, mode, both SHAs, coverage status, verdict, short rationale, confidence, checks, limits and open-finding status. Mark partial, failed, interrupted or cancelled reviews as incomplete; do not describe them as complete diff reviews. Put each finding's evidence, impact and correction in its review comment once; do not repeat full findings or investigation narratives in the summary. Keep enough evidence to assess the verdict.

Distinguish a recommended verdict from a submitted GitHub review. Report coverage completion separately from publication completion. Complete required publication before reporting the review as submitted; include the script's reviewer, commit, state and review link. If submission did not occur, state the concrete blocker. When either full stage completes, emit a compact checkpoint in chat with PR, phase, pinned base/head, the full profile and actual settings, coverage/verdict, open finding slugs and the current diff phase cursor with its source. Update the saved phase and cursor in later correction results. Do not post this record as a GitHub comment. After approval, report both available full-stage checkpoints and latest accepting diff range, if any, and the approval link. If that approval was already published for the current head, report the existing link instead of calling the script again.
