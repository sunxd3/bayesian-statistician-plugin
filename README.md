# Bayesian Statistician Plugin

Claude Code plugin for Bayesian statistical modeling workflows with Stan and ArviZ.

## Usage

```bash
git clone https://github.com/sunxd3/bayesian-statistician-plugin.git

claude --plugin-dir ./bayesian-statistician-plugin
```

Then invoke the `/bayesian-workflow` skill to start:

```
> /bayesian-workflow
> Analyze the dataset in data/sales.csv and build a Bayesian model
```

The skill activates the full Bayesian workflow: EDA → Model Design → Fitting → Validation → Reporting, with parallel subagents.

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
