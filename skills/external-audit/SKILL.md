---
name: external-audit
description: Run parallel adversarial PR reviews when the user asks to external-audit a PR or invokes /external-audit. Start with full reviews, use diff reviews after fixes, and require fresh final full reviews from both roles before PAT-backed approval. Publish deduplicated inline change requests when needed.
---

# External Audit

An invocation authorizes adversarial reviews and formal GitHub reviews through the private scripts. Findings belong inside reviews, not standalone comments. Keep verdict explanations and global feedback in chat. Do not merge or authorize code changes through this skill alone. Resolve the PR URL from the request or unambiguous context; ask if the target is ambiguous.

## Reviewer configuration

Change reviewer models and settings only in this table. Use the role and profile names everywhere else.

| Profile | Role | Provider | Model | Reasoning effort | Mode |
| --- | --- | --- | --- | --- | --- |
| `openai-deep` | `openai` | Codex | `gpt-6.1-sol` | high | regular |
| `anthropic-deep` | `anthropic` | Anthropic | `claude-opus-5-5` | high | regular |
| `openai-shallow` | `openai` | Codex | `gpt-6-luna` | max | regular |
| `anthropic-shallow` | `anthropic` | Anthropic | `claude-sonnet-5-5` | xhigh | regular |

Use each role's deep profile for `initial-full`, requested `full`, and `final-full` reviews. Use its shallow profile for `diff` reviews. For a targeted finding re-check, use the profile of the review being re-checked. Shallow profiles retain the same finding and evidence standards.

Resolve the exact provider IDs and supported options from runtime capabilities. Set the configured model, effort and mode explicitly; do not inherit settings that can enable fast mode. If a required configuration is unavailable, report the limitation; do not substitute another model.

In T3 Code, use `orchestrator_capabilities` before the first `delegate_task`, pass settings in `target.options`, and follow returned continuation instructions. Use supported delegation tools in other runtimes. Start a fresh agent for every review or re-check, without inherited conversation or implementation context. Reviewers never implement fixes or publish to GitHub.

## Track each reviewer separately

Keep a per-PR record for each role: last completed review SHA, last accepted SHA, review profile, mode and range, unresolved findings, and publication results. History belongs to the provider role, not the profile: switching between shallow and deep preserves its cursor and open findings. Track a final-full cycle ID and its results separately from initial or diff acceptance. Recover this record from prior chat audit records and submitted reviews before starting. Match older role labels by their recorded provider or model so a rename does not reset history. Record each result even when publication failed. A completed review that requests changes advances that role's completed-review SHA, but does not clear its findings or count as acceptance. An interrupted or incomplete run does not advance it.

Outside the mandatory final-full stage below, a repeat request uses a diff audit even if the user says only "audit this PR" or invokes `/xaudit` or `/external-audit` again:

- `first-range` Each role's first review uses mode `initial-full` and the real PR base to current head. For a stacked PR, use that layer's base. A role with no prior review must cover the full PR even if the other role has already reviewed it.
- `repeat-range` Correction reviews use mode `diff` and that role's own last completed review SHA to current head. Never use the other role's cursor or reset to the PR base.
- `full-range` An explicit full-audit request uses mode `full` and the real PR base for both roles in parallel. It overrides the repeat-range default.
- `final-range` The final approval stage always uses the real PR base to current head for both roles, with mode `final-full`. For a stacked PR, use that layer's base. It is a new review of the whole PR, including unchanged code and interactions between corrections.

If a repeat review has no recoverable previous SHA for that role, ask for it. Fetch an unavailable commit; do not replace it with a merge base or start an unrequested full audit. Compare the supplied commits directly. Reuse a completed result for an unchanged range and stage. Final-full results also require the same cycle ID; initial or diff acceptance cannot satisfy this stage. A specific finding re-check can use that role's prior range and closure checklist at the same head; an empty diff is not proof of correction. An unpublished or failed review can still be completed under the publication rules below.

Supply only [the auditor prompt](references/auditor-prompt.md) unchanged, repository location, PR URL, role, profile, audit mode and both SHAs. Include a minimal checklist of still-open findings and closure conditions so earlier defects cannot disappear outside a new diff. Do not supply old review prose, conversation history, implementation claims or author-proposed solutions. The reviewer must verify the checklist against code and tests independently.

- `stable-prefix` Put the unchanged auditor prompt first in every delegation, then append the role, profile, repository, PR, mode, SHAs and finding checklist in a consistent order. Keep tool definitions and configured model settings stable within each profile where the runtime permits. This can support prefix-cache reuse without inherited conversation. Cache controls belong to the runtime; do not invent options, resume old reviewers or add unrelated context to obtain a cache hit.

## Run parallel reviews

- `parallel-round` Start fresh `openai` and `anthropic` agents together for the initial full review and each correction round, using each role's own applicable range and the same target head. A role's acceptance never gates the other role's start. Reuse completed results only for the same range and stage; run missing reviews or explicit re-checks as needed.
- `correction-round` Collect both results before making authorized corrections. If either role requires changes at any stage, publish the combined required findings once. After fixes, run diff reviews in parallel until both roles accept the same head with no open required findings. A failed or unavailable peer blocks approval, but does not block publication of the other role's valid findings.
- `final-full` Once both roles accept the initial, requested full or diff review, start a new final-full cycle with two fresh agents in parallel over the entire PR. Resume an incomplete cycle by retrying only missing roles. This separate stage is mandatory even when both initial full reviews pass immediately at the unchanged head. If either final-full review requires changes, publish the findings, return to fix-and-diff rounds, and require a new final-full cycle after both diff reviews accept.
- `approve-round` Run `approve` only after both final-full reviews in the same cycle accept the current PR base and head with no unresolved required findings. Recheck the range before publication and approval. Any new commit or changed final-review base invalidates final-full acceptance; a new head needs diff consensus followed by fresh final-full reviews.

The parent may implement corrections only when the user has authorized that work. If fixes are authorized, continue the fix/review loop until both final-full reviews accept. Otherwise, report the findings after publication and resume parallel diff reviews when a later request supplies fixes. Do not make edits or merges merely to finish an audit.

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

After both final-full reviews in the same cycle accept the current PR base and head with no unresolved required findings, run the approval script once with exactly one argument, the PR URL. Initial or diff acceptance alone never authorizes this call:

```sh
EXTERNAL_AUDIT_REVIEWED_HEAD='REVIEWED_HEAD_SHA' 'APPROVE_SCRIPT_PATH' 'https://github.com/OWNER/REPO/pull/NUMBER'
```

Both scripts load `API_KEY` from their adjacent `.env`. Do not read that file, load `~/.zshrc`, print credentials, or substitute normal-connection review calls. The PAT account must differ from the PR author. Never publish separate inline comments, top-level PR comments or an additional approval summary.

After a failed or uncertain response, check existing reviews before retrying and recheck the head to avoid duplicates or reviewing an unaudited commit. Report publication failures and unpublished findings in chat; do not change the verdict to make publication succeed.

- `compact-results` After each review, give one compact chat result with the role, profile, mode, final-full cycle ID when applicable, both SHAs, verdict, short rationale, confidence, checks, limits and open-finding status. Put each finding's evidence, impact and correction in its review comment once; do not repeat full findings or investigation narratives in the summary. Keep enough evidence to assess the verdict.

Distinguish a recommended verdict from a submitted GitHub review. Complete required publication before reporting that round as complete; include the script's reviewer, commit, state and review link. If submission did not occur, state the concrete blocker. After final approval, report both roles' final-full range and the approval link. If that approval was already published for the current head, report the existing link instead of calling the script again.
