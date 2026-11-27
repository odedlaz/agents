---
name: ship-it
description: Use when carrying implementation work through frequent commits, draft PR creation, simplicity and performance sweeps, external audit approval, and a mergeable PR.
---

# Ship It

Commit early and often. Commit after every iteration and push every commit.
If no PR exists, create a draft PR immediately after the first commit.

Once the implementation is fully complete and no pending implementation tasks
remain, review the entire PR from scratch, focusing on simplicity,
maintainability, and performance:

- `simplicity-sweep` Ensure the implementation adheres to KISS, YAGNI, and DRY
  principles. Eliminate unnecessary complexity, abstractions, and over-engineering.
- `performance-sweep` Perform a performance sweep to identify and address
  low-hanging fruits. Prioritize straightforward, meaningful improvements without
  introducing unnecessary complexity or premature optimizations.

Only after the implementation is complete and both sweeps are finished, run an
external auditor using [external-audit](../external-audit/SKILL.md). Address all
findings and repeat the audit until approval is granted. Do not initiate the
audit prematurely. The goal is to minimize audit cycles by presenting a complete,
refined implementation for auditing.

Once approved, mark the PR as ready for review and drive it to green, addressing
all outstanding checks and review feedback until it is mergeable.

Once the PR is mergeable, load core:pr-style and rewrite the PR title and
description entirely from scratch, without reading their existing content.

Never merge a release-me PR under any circumstances, even if explicitly
authorized by the user.
