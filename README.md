# Agents

Personal skills distributed as an `agents` plugin for Claude Code and Codex.
Both clients load the same `skills/` directory.

## Install in Claude Code

```sh
claude plugin marketplace add odedlaz/agents
claude plugin install agents@agents
```

Start a new session, then invoke `/agents:external-audit` or
`/agents:self-improvement`.

## Install in Codex

```sh
codex plugin marketplace add odedlaz/agents
codex plugin add agents@agents
```

Start a new session and invoke `$external-audit`, or select the skill from the
plugin's skill picker.

## Skills

- `external-audit` Two independent adversarial code reviews using
  `claude-opus-5-5` and `gpt-6.1-sol`, both at high effort in regular mode.
  Auditors may exchange ideas and each posts its own required inline findings.
  Approval runs through the private script only after both accept. This workflow
  requires cross-provider delegation, such as T3 Code; installing the plugin
  alone does not add a delegation tool or access to either model.
- `self-improvement` Research and propose improvements to the user's local
  Claude Code instructions. This skill remains specific to Claude Code.

## Approval credentials

`external-audit/approve` loads `API_KEY` from a `.env` file beside the script.
Use an account that can approve the target PR; GitHub rejects self-approval.
Configure this file separately in each installed copy. `.env` files are ignored
by git and are not included in the marketplace. Inline findings use the normal
GitHub connection. Reviewers never load the approval credentials.

## Local development

Register a checkout instead of GitHub by passing its absolute path to
`claude plugin marketplace add` or `codex plugin marketplace add`.

For direct Claude skill links, `./scripts/setup.sh` links every skill into
`${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/`. It does not manage global instruction
files. Avoid installing both direct links and the plugin in the same client.

```sh
claude plugin validate .
claude plugin validate .claude-plugin/marketplace.json
codex plugin list --marketplace agents --available --json
```

Update the plugin version in both manifests when publishing changes.
Marketplace formats follow the [Claude Code marketplace reference](https://code.claude.com/docs/en/plugin-marketplaces)
and [Codex plugin packaging documentation](https://developers.openai.com/plugins/build/plugins).
