---
name: python-environment
description: Python environment setup with uv, the bundled shared_utils library, and script structure guidelines.
user-invocable: false
---

# Python Environment

**Always use `uv`.** Never use bare `python`/`pip`, never search for a Python interpreter, never create a virtual environment by hand. `uv run` resolves the environment from the nearest `pyproject.toml` up the directory tree.

## Environment Setup

The Bayesian workflow needs a project with Stan/ArviZ dependencies plus the bundled `shared_utils` library. Do this **once**, at the start of a workflow, from the working directory. If `./shared_utils/` and `pyproject.toml` already exist, the environment is set up — skip to running scripts.

1. Copy the bundled `shared_utils` package into the project so it survives plugin updates and is a stable path dependency:

   ```bash
   cp -r "${CLAUDE_SKILL_DIR}/shared_utils" ./shared_utils
   ```

2. Create `pyproject.toml` in the project root (if one already exists, merge these `dependencies` and the `[tool.uv.sources]` entry into it):

   ```toml
   [project]
   name = "bayesian-analysis"
   version = "0.0.0"
   requires-python = ">=3.11"
   dependencies = [
       "arviz>=0.17.0,<1.0.0",
       "cmdstanpy>=1.2.0",
       "numpy>=1.26.0",
       "pandas>=2.0.0",
       "matplotlib>=3.8.0",
       "scipy>=1.11.0",
       "seaborn>=0.13.0",
       "shared-utils",
   ]

   [tool.uv.sources]
   shared-utils = { path = "./shared_utils" }
   ```

3. Sync the environment and install the CmdStan toolchain (CmdStanPy compiles Stan models against it):

   ```bash
   uv sync
   uv run python -m cmdstanpy.install_cmdstan
   ```

After setup, run every script from the project root:

```bash
uv run python experiments/experiment_X/fit/run_fit.py
```

The environment provides `arviz`, `cmdstanpy`, `numpy`, `pandas`, `matplotlib`, `scipy`, `seaborn`, and `shared_utils`. `scikit-learn`, `statsmodels`, and deep-learning frameworks are intentionally excluded — the workflow is Stan-based (see the `bayesian-workflow` skill). Add a dependency to `pyproject.toml` only if a model genuinely requires it.

## Shared Utilities

`shared_utils` is the bundled helper library. Import directly — do not modify it:

```python
# Preferred: fit-and-summarize pipeline (auto-cleans CSVs, returns structured results)
from shared_utils import fit_and_summarize, FitResult

# Stan/CmdStanPy utilities (lower-level, use when you need manual control)
from shared_utils import compile_model, fit_model

# Diagnostics
from shared_utils import check_convergence, compute_loo, get_divergences
from shared_utils import ConvergenceResult, LOOResult

# Prior predictive (ArviZ conversion for GQ-only Stan programs)
from shared_utils import to_arviz_prior

# JSON I/O (auto mkdir, handles numpy types) and CSV cleanup
from shared_utils import write_json, NumpyEncoder, cleanup_csv_files

# Path utilities
from shared_utils import ensure_dir, resolve_path, project_root
```

**Key features:**
- `fit_and_summarize(model, stan_data, model_name=..., save_dir=...)` — preferred workflow for posterior fitting. Fits the model, computes summary/diagnostics/LOO, returns a `FitResult`. CSVs are always cleaned up after extraction (5-500 MB/chain, nothing lost). Pass `save_netcdf=True` for main data fits — the `.nc` (5-50 MB) preserves `y_rep` and `log_lik` draws needed for PPC, LOO-PIT, and `az.compare()`. Skip `.nc` for probes and recovery runs.
- `FitResult` fields: `param_summary` (DataFrame), `convergence` (ConvergenceResult), `loo` (LOOResult or None), `thinned_draws` (dict of parameter-only arrays — NO `y_rep` or `log_lik`), `diagnostics` (dict), `warnings` (list). Call `result.save(dir)` to write JSON artifacts.
- `to_arviz_prior(fit, prior_predictive=["y_rep"], observed_data=...)` — converts a `fixed_param` fit of a GQ-only `prior_model.stan` to ArviZ InferenceData with `prior` and `prior_predictive` groups. See the `stan-coding` skill for the full workflow.
- `fit_model(model, data, iter_warmup=1000, iter_sampling=1000, ...)` — lower-level, matches the CmdStanPy API. Use when you need the raw `CmdStanMCMC` object. Validates `iter_warmup > 0` when `adapt_engaged=True`, and that `data` is a dict.
- `write_json(path, data)` — write JSON to disk (auto-creates parent directories, uses `NumpyEncoder` for numpy types, indent=2). Prefer over raw `json.dump()` + `open()`.
- `NumpyEncoder` handles `numpy.bool_` and other numpy scalars for JSON serialization (used internally by `write_json`).

For the full API, read the package source in this skill's `shared_utils/src/shared_utils/` directory.

## Script Structure

Write small, focused scripts — not monolithic files. Separate concerns:

```
experiments/experiment_X/
  fit/
    run_fit.py        # Main entry point
    diagnostics.py    # Convergence checks
    plots.py          # Visualization
  model.stan          # Stan model
```

Each script should:
- Do one thing well
- Be runnable via `uv run python script.py` from the project root
- Import shared logic from `shared_utils` instead of rewriting common patterns
- Use paths relative to the project root and write outputs into the canonical folder structure

**Common imports pattern:**
```python
#!/usr/bin/env python
"""Model fitting script."""
from pathlib import Path

from shared_utils import compile_model, fit_and_summarize

# Script logic here...
```
