# Bayesian Statistician Plugin

Claude Code plugin for Bayesian statistical modeling workflows with Stan and ArviZ.

## Usage

```bash
git clone https://github.com/sunxd3/bayesian-statistician-plugin.git

claude --system-prompt "$(cat ./bayesian-statistician-plugin/system_prompt.md)" --plugin-dir ./bayesian-statistician-plugin
```

Without `--system-prompt`, the skills and agents are available but Claude won't automatically orchestrate the full workflow. With the system prompt, Claude follows the structured Bayesian workflow (EDA → Model Design → Fitting → Validation → Reporting) and uses parallel subagents.

Then ask Claude to do Bayesian analysis:

```
> Analyze the dataset in data/sales.csv and build a Bayesian model
```

## Optional Settings

Add to your `.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR": "1",
    "CLAUDE_CODE_SUBAGENT_MODEL": "claude-opus-4-5-20251101"
  }
}
```

- `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR`: Resets working directory to project root after each bash command
- `CLAUDE_CODE_SUBAGENT_MODEL`: Model for subagents (default is sonnet)
