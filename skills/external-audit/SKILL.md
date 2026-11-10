---
name: external-audit
description: Run staged adversarial PR reviews when the user asks to external-audit a PR or invokes /external-audit. Run fast until it accepts, then slow. Publish PAT-backed change requests with inline findings, or approve when both accept the same head.
---

# External Audit

An invocation authorizes adversarial reviews and formal GitHub reviews through the private scripts. Findings belong inside reviews, not standalone comments. Keep verdict explanations and global feedback in chat. Do not merge or authorize code changes through this skill alone. Resolve the PR URL from the request or unambiguous context; ask if the target is ambiguous.

## Reviewer configuration

Change reviewer models and settings only in this table. Use the role names everywhere else.

| Role | Provider | Model | Reasoning effort | Mode |
| --- | --- | --- | --- | --- |
| `fast` | Codex | `gpt-6.1-sol` | high | regular |
| `slow` | Anthropic | `claude-opus-5-5` | high | regular |

`fast` and `slow` are role names, not service tiers. Resolve the exact provider IDs and supported options from runtime capabilities. Set the configured model, effort and mode explicitly; do not inherit settings that can enable fast mode. If a required configuration is unavailable, report the limitation; do not substitute another model.

In T3 Code, use `orchestrator_capabilities` before the first `delegate_task`, pass settings in `target.options`, and follow returned continuation instructions. Use supported delegation tools in other runtimes. Start a fresh agent for every review or re-check, without inherited conversation or implementation context. Reviewers never implement fixes or publish to GitHub.

## Track each reviewer separately

Keep a per-PR record for each role: last completed review SHA, last accepted SHA, unresolved findings, and publication results. Recover this record from prior chat audit records and submitted reviews before starting. Record each result even when publication failed. A failed review advances that role's completed-review SHA, but does not clear its findings or count as acceptance.

A repeat request uses a diff audit even if the user says only "audit this PR" or invokes `/xaudit` or `/external-audit` again:

- `first-range` Each role's first review uses the real PR base to current head. For a stacked PR, use that layer's base. The second role's first review must cover all earlier commits, not just the last correction.
- `repeat-range` Later reviews use that role's own last completed review SHA to current head. Never use the other role's cursor or reset to the PR base.
- `full-range` An explicit full-audit request uses the real PR base for both roles, with the same stage order. It overrides the repeat-range default.

If a repeat review has no recoverable previous SHA for that role, ask for it. Fetch an unavailable commit; do not replace it with a merge base or start an unrequested full audit. Compare the supplied commits directly. If that role already reviewed the unchanged head, reuse its recorded result instead of starting another agent. A specific finding re-check can use that role's prior range and closure checklist at the same head; an empty diff is not proof of correction. An unpublished or failed review can still be completed under the publication rules below.

Supply only [the auditor prompt](references/auditor-prompt.md) unchanged, repository location, PR URL, role, audit mode and both SHAs. Include a minimal checklist of still-open findings and closure conditions so earlier defects cannot disappear outside a new diff. Do not supply old review prose, conversation history, implementation claims or author-proposed solutions. The reviewer must verify the checklist against code and tests independently.

## Run the stages

- `fast-stage` Start with `fast`, including the very first audit. Do not start `slow` in parallel. If `fast` returns `REQUEST CHANGES`, publish its required findings and return them for correction. When fixes are available, review the new diff with a fresh `fast` agent. Repeat this stage until `fast` accepts the current head.
- `slow-stage` Start `slow` only after `fast` accepts the current head. Use `slow`'s own first or repeat range. If `slow` returns `REQUEST CHANGES`, publish its required findings and return to the fast stage after fixes. Do not send the fixes directly to `slow` without a current-head fast acceptance.
- `approve-stage` Run `approve` only when both roles accept the same current head and no required findings remain open. Any new commit returns the workflow to the fast stage. Recheck the head before publication and approval; a changed head needs the applicable diff reviews.

The parent may implement corrections only when the user has authorized that work. If fixes are authorized, continue the fix/review loop until both roles accept. Otherwise, report the findings after publication and resume the fast stage when a later request supplies fixes. Do not make edits or merges merely to finish an audit.

Either role can require a correction independently. Agreement on individual findings is not required; consensus means both accept the final commit. Keep prior findings open until their corrections are explicitly verified, including findings outside the current diff. Missing evidence, failed reviews, ambiguous verdicts and publication failures cannot count as acceptance. If the parent disputes a finding, keep it open and obtain a fresh re-check instead of discarding it or forcing agreement.

## Publish and report

Only the parent runs the private scripts. Resolve `approve` and `request-changes` beside this `SKILL.md` and use their absolute paths.

For either role's `REQUEST CHANGES`, submit one formal review containing its required findings. Merge reports of the same underlying defect, even when wording, slugs or nearby anchors differ. Keep distinct defects separate, including those on the same line. Assign one stable slug and one inline comment per defect. Do not repost an unchanged finding already present in an open review; report its existing link and keep it open.

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

Do not run the approval script after the first stage alone. After both roles accept the same current head with no unresolved required findings, run it once with exactly one argument, the PR URL:

```sh
EXTERNAL_AUDIT_REVIEWED_HEAD='REVIEWED_HEAD_SHA' 'APPROVE_SCRIPT_PATH' 'https://github.com/OWNER/REPO/pull/NUMBER'
```

Both scripts load `API_KEY` from their adjacent `.env`. Do not read that file, load `~/.zshrc`, print credentials, or substitute normal-connection review calls. The PAT account must differ from the PR author. Never publish separate inline comments, top-level PR comments or an additional approval summary.

After a failed or uncertain response, check existing reviews before retrying and recheck the head to avoid duplicates or reviewing an unaudited commit. Report publication failures and unpublished findings in chat; do not change the verdict to make publication succeed.

After every completed review, report the role, mode, both SHAs, verdict, rationale, confidence, checks, limits and open findings in chat. Distinguish a recommended verdict from a submitted GitHub review. Complete required publication before reporting that stage as complete; include the script's reviewer, commit, state and review link. If submission did not occur, state the concrete blocker. After final approval, report both roles' accepted SHA and the approval link. If that approval was already published for the current head, report the existing link instead of calling the script again.
