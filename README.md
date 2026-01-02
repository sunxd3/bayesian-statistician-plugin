# Bayesian Statistician Plugin

Claude Code plugin providing specialized subagents and skills for Bayesian statistical modeling workflows.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/xiandasun/bayesian-statistician-plugin.git

# Launch Claude Code with the plugin
claude --plugin-dir ./bayesian-statistician-plugin
```

Then just ask Claude to do Bayesian analysis - the `bayesian-workflow` skill auto-invokes:

```
> Analyze the dataset in data/sales.csv and build a Bayesian model
```

## Installation Options

### Option 1: Local directory (recommended for testing)

```bash
claude --plugin-dir /path/to/bayesian-statistician-plugin
```

### Option 2: Install as plugin

```bash
/plugin marketplace add xiandasun/bayesian-statistician-plugin
/plugin install bayesian-statistician@xiandasun/bayesian-statistician-plugin
```

## What's Included

### Orchestration Skill

| Skill | Description |
|-------|-------------|
| `bayesian-workflow` | Full orchestration workflow (EDA → Model Design → Fitting → Validation → Reporting). Auto-invokes on Bayesian modeling tasks. |

### Subagents

| Agent | Description |
|-------|-------------|
| `eda-analyst` | Exploratory data analysis for Bayesian modeling |
| `model-designer` | Proposes candidate Bayesian models |
| `model-fitter` | Fits Stan models via CmdStanPy |
| `model-critique` | Assesses model fit and suggests improvements |
| `model-refiner` | Refines models based on critique |
| `model-selector` | Compares models via LOO/WAIC |
| `prior-predictive-checker` | Validates prior predictive distributions |
| `posterior-predictive-checker` | Validates posterior predictive checks |
| `recovery-checker` | Parameter recovery simulation |
| `report-writer` | Generates final analysis reports |
| `decision-auditor` | Audits model selection decisions |

### Technical Skills

| Skill | Description |
|-------|-------------|
| `stan-coding` | Best practices for writing Stan programs |
| `visual-predictive-checks` | Guidelines for predictive check visualizations |
| `convergence-diagnostics` | MCMC convergence diagnostic guidelines |
| `artifact-guidelines` | Standards for analysis artifacts |
| `stan-ode-modeler` | ODE modeling in Stan |

## Technical Stack

- **Inference**: Stan via CmdStanPy
- **Diagnostics**: ArviZ
- **Package management**: uv

## Workflow Overview

The `bayesian-workflow` skill orchestrates a multi-phase analysis:

1. **Phase 1: EDA** → `eda/` - Data exploration with parallel analysts
2. **Phase 2: Model Design** → `experiments/experiment_plan.md` - Propose competing models
3. **Phase 3: Model Development** → `experiments/` - Validate, fit, critique, refine
4. **Phase 6: Reporting** → `final_report.md` - Generate final report

Each phase uses specialized subagents that communicate via files.
