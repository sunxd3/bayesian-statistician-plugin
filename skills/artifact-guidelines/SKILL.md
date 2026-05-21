---
name: artifact-guidelines
description: Guidelines for writing reports, organizing files, and generating code artifacts
user-invocable: false
---

# Report Writing and File Organization

This skill provides best practices for all subagents when generating written artifacts, code files, and figures.

## Writing Guidelines

Use GitHub-flavored CommonMark markdown for all text outputs (reports, logs, documentation). Never use plain .txt files.

Write concisely:
- Short paragraphs with complete sentences
- Favor insight over exhaustiveness
- Use lists sparingly, only when they genuinely clarify (e.g., model assumptions, validation criteria)
- Avoid markdown overuse - minimal headers and bold, no excessive formatting

In reports:
- Lead with key findings or conclusions
- Support claims with evidence (plots, statistics, diagnostics)
- Reference files with clear relative paths: "As shown in `figures/washout_curves.png`..." or "`washout_curves.png`" if in same directory
- Document what you tried, what worked, and what didn't

In logs:
- Capture decisions and reasoning, not play-by-play execution
- Record why you chose certain paths or skipped alternatives
- Note failures and how you addressed them

Use scratchpad:
- You should create local files to write a first draft, including thinking process
- Rewrite it to form final output, then delete the temporary local files you created 

## Directory Structure

**CRITICAL**: Always use the standardized directory structure:

```
data/             # Source data files
eda/              # Exploratory data analysis
design/           # Model design: designer outputs and experiment plan
experiments/      # Model development and execution
final_report.md   # Final deliverable
log.md            # Decision log
```

Use **relative paths** from the project root (not absolute paths). The system prompt defines this canonical structure. Scripts should reference files using relative paths like `eda/eda_report.md` or `experiments/experiment_1/fit/`.

## Code Organization

One logical unit per file:
- One model per .stan file
- One analysis per .py script
- Descriptive names: `fit_hierarchical_model.py` not `model.py`
- Self-contained scripts that run independently
- Save outputs to appropriate subdirectory: `eda/` for exploration, `experiments/` for models

**Stan only:** All Bayesian models must use Stan via CmdStanPy. Do not use PyMC, NumPyro, Pyro, or other PPLs.

Keep it simple:
- No deep nesting of directories unless natural grouping exists
- Clean up exploratory scripts after consolidating insights into reports
- Every file should have a clear purpose

## Figure Organization

Save figures within their respective phase directories using descriptive filenames:
- `eda/distributions.png` for EDA plots
- `experiments/experiment_1/prior_predictive/prior_check.png` for experiment plots
- Use descriptive names: `group_washout_curves.png` not `fig1.png`

One figure per concept or question:
- Avoid packing too many subplots (max 2x2 for comparisons)
- Save at appropriate resolution (300 DPI for reports, 150 for exploratory)
- Reference figures in reports using relative paths: `eda/distributions.png`

## File Minimalism

Generate fewer, better files:
- Consolidate related content - one EDA report, not 10 partial analyses
- Combine related visualizations into multi-panel figures when appropriate
- Only create files that will be read by users or subsequent agents
- Remove intermediate artifacts after they've served their purpose

Each file you create should justify its existence. Ask: will this be read? Does it convey unique information?

## Reporting Back to Main Agent

Your response message to the main agent shares its context window with all other subagents' responses. Keep it short to avoid overwhelming the orchestrator.

**Write details to files, return only a summary.** Put all substantive content — findings, diagnostics, reasoning, evidence — into your output files (reports, assessment files). Your response message should be a brief handoff, not a repeat of what's in the files.

**Response format** — use these exact headers (aim for 10-20 lines total):

```
### Outcome
PASS/FAIL/VIABLE/BROKEN or equivalent status + 1-2 sentence key finding.

### Files Created
- `path/to/file.md` — one-line description
- `path/to/plot.png` — one-line description

### Issues
Anything the main agent needs to act on, or "None".
```

**Do not** restate report contents, include full diagnostic tables, reproduce code snippets, or explain your methodology in the response. The main agent will read your files if it needs details.
