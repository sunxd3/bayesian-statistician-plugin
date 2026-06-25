---
description: Run exploratory data analysis on a dataset for Bayesian modeling. Standalone — can be used independently of the full /bayesian-workflow:run pipeline.
argument-hint: "<data_path> [output_dir] [--focus=<area>]"
allowed-tools: Agent, Bash, Read
---

Run the `eda-analyst` subagent on `$ARGUMENTS`. The agent profiles the dataset, completes the data semantics audit, applies standardization, investigates competing data-generating stories, and produces a modeling handoff report.

## Parse arguments

From `$ARGUMENTS`, extract:
- `data_path` (required, first positional) — path to the dataset (CSV, JSON, Parquet)
- `output_dir` (optional, second positional; default `eda/`) — directory to write outputs into
- `focus_area` (optional, `--focus=<area>` or trailing prose) — aspect of the data to emphasize

If `$ARGUMENTS` is empty or `data_path` cannot be identified, ask the user for the dataset path and stop.

## Verify environment

Use Bash to check that `./pyproject.toml` and `./shared_utils/` both exist in the current working directory. If either is missing, tell the user to run `/bayesian-workflow:setup` first and stop.

## Invoke eda-analyst

Use the `Agent` tool with `subagent_type: eda-analyst`. The prompt should convey the parsed args clearly so the subagent's input validation passes — for example:

> Run EDA on the dataset at `<data_path>`. Write outputs to `<output_dir>`. Focus area: `<focus_area>` (or "none").

The subagent validates inputs per `validation-protocol` and follows its own workflow.

## Present results

When the subagent returns, present the summary to the user. Point them at:
- `<output_dir>/eda_report.html` — full narrative report (open in a browser)
- `<output_dir>/log.md` — append-only running trace of the workflow
- `<output_dir>/data.cleaned.parquet` — canonical cleaned dataset
