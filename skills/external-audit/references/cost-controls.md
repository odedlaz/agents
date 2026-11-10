# Runtime cost controls

Use these controls only where the active runtime supports them. Do not invent delegation options, change global settings, resume old reviewers, or share conclusions to obtain cache hits. Keep the configured models, effort, regular mode, fresh agents and review coverage. If controls are unavailable, continue with the supported workflow and state the limit when reporting savings.

## Stable inputs and tools

Keep system instructions and tool definitions in a fixed order within each provider and profile. Append changing task data after the auditor prompt. Do not insert timestamps or random IDs into the stable prefix. Within one reviewer run, append updates instead of rewriting earlier context. Do not assume cache reuse across models, profiles or providers.

For large tool catalogs, prefer supported tool search or deferred loading. Keep essential search and read tools available. Choose the tool set before the run; do not repeatedly add, remove or reorder definitions. Do not copy the full catalog into the prompt. Anthropic deferred tools cannot carry cache breakpoints; use supported breakpoints on non-deferred content. See [OpenAI tool search](https://developers.openai.com/api/docs/guides/tools-tool-search) and [Anthropic tool search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool).

## Cache lifetime

Use observed reuse intervals, including response-generation and tool time, to compare write premiums with avoided rewrites. Prefer the shorter supported lifetime when it covers expected reuse; choose longer retention only when expected reuse justifies its premium. Do not send keepalive requests only to warm the cache. Product subscriptions can use different policies from the APIs; verify actual usage rather than assuming API settings control the host.

- `openai-cache` The current Responses API supports 30-minute and 12-hour lifetimes, with total write rates of 1.25× and 2.5× uncached input respectively. These are total rates, not added surcharges. Use only options exposed by the runtime. See [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).
- `anthropic-cache` The Messages API supports five-minute and one-hour caching. Reads refresh expiry; the interval starts at the request start, so generation time counts. A longer lifetime can waste its write premium on a short-lived reviewer. See [Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).

## Tool results and context

Use the auditor prompt's bounded reads and batching. Existing code orchestration can filter large tool results before they enter context; retain relevant errors, exit codes, locations and retrievable full evidence. It must not discard unreviewed scope. See [Anthropic advanced tool use](https://www.anthropic.com/research/advanced-tool-use).

Use supported context editing or compaction when context pressure requires it. Preserve SHAs, remaining coverage, open findings, closure evidence and check results. Clearing results or thinking can invalidate cached prefixes and cause new writes. Prefer the host's supported compaction; do not build a separate summarizer or inherit another reviewer's context for savings. See [Anthropic context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing).

## Review-specific controls

[Devin](https://devin.ai/blog/devin-review-2) and [Bugbot](https://cursor.com/blog/bugbot-updates-june-2026) use incremental reviews to avoid repeated work. Keep each profile's own SHA cursor and reuse valid completed results. Do not add a final/full-PR review to obtain confidence or cache reuse. [CodeRabbit](https://www.coderabbit.ai/blog/the-art-and-science-of-context-engineering) verifies proposed findings against repository context. Use the auditor prompt's evidence check within each existing reviewer, without adding another routine model pass. Inspect evident high-risk paths first, but finish the assigned scope and collect all required findings before returning a normal verdict.

## Measure results

For model or workflow trials, verify the loaded prompt and settings rather than grouping by launch date alone. Compare reviewer cost and wall-clock time per completed PR, review-round counts, incomplete retries and confirmed useful findings. Measure low-stage rejection rates, incremental high-stage findings and clean cycles that run all four profiles. Include rejected cycles and retries; label unfinished PRs and unknown active usage separately. Different PR sizes and scopes limit causal comparisons.

Record available input, cached reads, cache writes by lifetime, output, elapsed time and pricing basis per profile. When available, also record initial context size and model-request count to separate host overhead from accumulated tool output. Deduplicate telemetry by provider message or tool-call ID before counting usage or repeated results. Distinguish reviewer usage from parent, fixes and auxiliary work. Missing counters are unknown, not zero. Compare matched review ranges and completed coverage before claiming savings; a higher cache-hit rate alone does not prove a lower total cost. Track confirmed useful findings, disproved findings, observed missed defects and review-round retries as well. Do not optimize only for fewer comments or treat an unaddressed finding as false without checking it.

The stable-prefix guidance also follows [OpenAI Prompt Caching 201](https://developers.openai.com/cookbook/examples/prompt_caching_201) and [Thariq Shihipar's caching post](https://x.com/trq212/status/2024574133011673516), read through its [public transcript](https://threadnavigator.com/thread/2024574133011673516/). [Boris Cherny's explanation](https://github.com/anthropics/claude-code/issues/46829?timeline_page=1) supports choosing lifetime from actual reuse. [Tibo's announcement](https://x.com/thsottiaux/status/2112712984644784534), read through a [public mirror](https://twstalker.com/thsottiaux/status/2112712984644784534), distinguishes API and product caching. These posts are context; the provider documentation defines supported controls.
