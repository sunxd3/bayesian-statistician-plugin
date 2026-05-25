---
description: Bootstrap the Python environment for the Bayesian workflow — copies the bundled `shared_utils` library into the project, creates `pyproject.toml`, syncs dependencies with `uv`, and installs CmdStan.
allowed-tools: Bash, Read, Write, Edit
---

Bootstrap the Python environment for the Bayesian workflow. Run once per project, from the working directory.

**Always use `uv`.** Never use bare `python`/`pip`, never create a virtual environment by hand.

## Idempotency check

If `./shared_utils/` and `./pyproject.toml` both already exist, the environment is set up — report this and stop.

## Steps

1. Copy the bundled `shared_utils` package into the project so it survives plugin updates and is a stable path dependency:

   ```bash
   cp -r "${CLAUDE_PLUGIN_ROOT}/shared_utils" ./shared_utils
   ```

2. Create `pyproject.toml` in the project root. If one already exists, merge the `dependencies` list and the `[tool.uv.sources]` entry into it rather than overwriting:

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

After setup, see the `python-environment` skill for the `shared_utils` API and script structure conventions.
