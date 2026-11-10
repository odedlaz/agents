---
name: external-audit
description: Run adversarial PR diff audits when the user asks to external-audit a PR or invokes /external-audit. Run sequential low-effort screening, then high-effort acceptance over separate profile diffs, with no full-PR stage. Publish deduplicated inline change requests or PAT-backed approval.
---

# External Audit

An invocation authorizes the automatic diff-review loop, incomplete-review retries, range recovery and formal GitHub reviews through the private scripts. Continue without asking for permission or a readiness decision. Explicit user pauses or limits override this authorization. Findings belong inside reviews, not standalone comments; keep verdict explanations and global feedback in chat. This skill does not authorize code edits or merges. Resolve the PR from the request or unambiguous context; ask if the target is ambiguous.

## Reviewer configuration

Change models and settings only in this table. Use profile and role names elsewhere.

| Profile | Role | Provider | Model | Reasoning effort | Mode |
| --- | --- | --- | --- | --- | --- |
| `openai-deep` | `openai` | Codex | `gpt-6.1-sol` | high | regular |
| `anthropic-deep` | `anthropic` | Anthropic | `claude-opus-5-5` | high | regular |
| `openai-shallow` | `openai` | Codex | `gpt-6.1-sol` | low | regular |
| `anthropic-shallow` | `anthropic` | Anthropic | `claude-opus-5-5` | low | regular |

Run profiles sequentially: `openai-shallow` → `anthropic-shallow` → `openai-deep` → `anthropic-deep`. Start the next profile only after complete acceptance at the preceding gates for the current base/head. A complete rejection skips all later profiles; after authorized corrections, restart at `openai-shallow`. All four profiles run mode `diff` with the same finding and evidence standards. Deep means higher effort, not a full-PR review. Do not overlap reviewers or add a full-PR stage.

Resolve provider IDs and supported options from runtime capabilities. Set configured model, effort and regular mode explicitly; do not inherit fast mode. If a configuration is unavailable, report the blocker without substituting a model. In T3 Code, call `orchestrator_capabilities` before the first `delegate_task`, pass settings in `target.options` and follow continuation instructions. Use supported delegation tools elsewhere. Every review or re-check starts a fresh agent without inherited conversation, implementation context or the other reviewer's verdict. Reviewers do not fix code or publish to GitHub.

## Track each reviewer separately

Keep per-PR, per-profile records: last completed review SHA and range, last accepted SHA, current PR base, provider/model/effort/runtime mode, coverage, open findings and publication results. Recover history from chat audit records and submitted reviews. Match older records by provider/model/effort/mode and coverage, not profile name alone. For example, an old shallow-profile review with settings that now match deep belongs to that deep profile; it does not establish a low-effort cursor. Preserve findings from every configuration.

Each of the four profiles owns a separate completed-review cursor. Never copy a cursor between profiles, including profiles from the same provider. Complete coverage advances only the reviewed profile's cursor, even on rejection or failed publication. For example, after a complete `anthropic-deep` rejection of C..D, its next range after fix E is D..E, plus open-finding closure checks. Partial, cancelled, failed and interrupted reviews never advance cursors. Preserve confirmed findings from incomplete work.

Low acceptance never advances deep cursors or substitutes for deep coverage. Deep profiles must review all changes since their own completed-review SHAs, including changes accumulated during low-only rounds. A profile without matching history starts from the actual PR base. Reuse complete results only when profile settings, reviewed code, range and finding-closure evidence still match. A new head or changed PR base invalidates current gate acceptance, but preserves completed-review cursors for range recovery. Old stage names such as `initial-full` and `final-full` describe history only; do not launch them.

## Select diff ranges

- `first-range` A profile with no completed review starts from the actual PR base to current head, mode `diff`. For stacked PRs, use that layer's base. This is its first review of changed PR code, not a separate full-PR approval pass.
- `repeat-range` A profile with history reviews its own last completed SHA to current head. Skipped profiles keep their cursors. When they eventually run, include all accumulated changes since their own cursors; never send only the latest low-effort correction diff.
- `base-changed` After a verified upstream merge or rebase adds upstream changes or makes a cursor invalid, automatically review the actual current PR base-to-head diff for affected profiles. Record the reason and retain old cursors until complete reviews replace them. Do not create a full-review stage or ask for permission to recover the range.
- `explicit-rescan` An explicit request to review all PR changes resets all four profiles' next diff ranges to the actual PR base and head. It still uses the four-profile sequence, with no additional final stage.

Fetch unavailable commits. Recover a missing cursor from history or ask for it; do not invent a SHA or silently reset an ordinary repeat diff. Compare supplied commits directly. An unchanged-head finding re-check can reuse its prior range and closure checklist; an empty diff alone does not prove correction. Relevant surrounding code and tests may be read to understand the diff, without reopening unrelated unchanged code as a new audit scope.

Supply only [the auditor prompt](references/auditor-prompt.md) unchanged, repository, PR URL, role, profile, mode `diff` and both range SHAs. Add the current PR base and a minimal checklist of all open required findings and closure conditions, including other profiles' and retired configurations' findings. Do not send old review prose, author-proposed solutions, conversation, implementation claims or peer conclusions. Each reviewer verifies findings independently. Earlier defects cannot disappear because they lie outside the current diff.

- `stable-prefix` Put the unchanged prompt first, then role, profile, repository, PR, mode, range SHAs, current PR base and checklist in that order. Keep supported system instructions, tool definitions and tool order stable. Cache reuse must not inherit conversation or conclusions. Read [runtime cost controls](references/cost-controls.md) when configuring cache, tools or context; use only supported controls without changing reviewer settings.

## Run the automatic diff loop

- `reuse-approval` Before launching, verify any existing published approval against the current base/head, all four configured profiles' complete accepting coverage and no open findings. If all match, report it without another review. Explicit rescans still rerun the requested diffs. Reuse independently valid current-head acceptances when retrying only missing work; do not reuse stale settings or coverage.
- `screen-openai` Start fresh `openai-shallow` on its outstanding diff. Complete the assigned scope and all open-finding checks before a normal verdict. Complete rejection publishes deduplicated findings and skips all later profiles.
- `screen-anthropic` After complete `openai-shallow` acceptance, recheck base/head and run fresh `anthropic-shallow` on its own outstanding diff. Rejection skips both deep profiles.
- `deep-openai` After both shallow profiles accept, recheck base/head and run fresh `openai-deep` on its own outstanding diff. Rejection skips `anthropic-deep`.
- `deep-anthropic` After all preceding profiles accept, recheck base/head and run fresh `anthropic-deep` on its own outstanding diff. Its acceptance completes the review gates; no whole-PR pass follows.
- `restart-after-findings` After any complete rejection, publish required findings and make corrections only when authorized. After corrections, restart at `openai-shallow`, then follow the sequence. Keep all completed-review cursors and verify every open required finding; restart does not reset coverage to the PR base. If fixes are not authorized, report the published findings and resume when fixes arrive.
- `incomplete-round` Preserve findings and retry the same profile with a fresh reviewer over the unchanged range until coverage completes. A partial report can support publication of confirmed findings, but cannot advance cursors, permit corrections or count as acceptance/rejection. Report and resolve concrete access/runtime blockers before retrying. A finding reported during an incomplete review blocks approval but does not force earlier gates to rerun before this profile completes. No retry count bypasses complete acceptance at earlier gates. Retry only missing work while preceding acceptances remain valid; otherwise restart the sequence.
- `approve-round` Run `approve` only after all four profiles have complete accepting coverage through the same current head, under the current PR base and configured settings, with no unresolved required findings. In particular, both deep acceptances are mandatory; low-only consensus cannot approve. Starting SHAs may differ because cursors are separate. Recheck base/head immediately before publication and approval. Missing or failed reviews block approval, but not valid finding publication.

Do not stop a reviewer at the first defect. Only fix code when authorized; if authorized, continue correction diffs until all four profiles accept. Otherwise report published findings and resume when fixes arrive. Keep findings open until verified, including those outside the latest diff. Missing evidence, ambiguous verdicts or publication failures cannot count as acceptance. Disputed findings require a fresh re-check rather than forced agreement or silent dismissal. Do not merge just to finish an audit.

## Publish and report

Only the parent runs the private scripts. Resolve `approve` and `request-changes` beside this `SKILL.md` and use their absolute paths.

For a round with `REQUEST CHANGES`, submit one formal review containing the required findings from either reviewer. Merge reports of the same underlying defect, even when wording, slugs or nearby anchors differ. Keep distinct defects separate, including those on the same line. Assign one stable slug and one inline comment per defect. Do not repost an unchanged finding already present in an open review; report its existing link and keep it open.

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

Distinguish a recommended verdict from a submitted GitHub review. Complete required publication before reporting that round as complete; include the script's reviewer, commit, state and review link. If submission did not occur, state the concrete blocker. After approval, report all four profiles' diff ranges and the approval link. If that approval was already published for the current head, report the existing link instead of calling the script again.
