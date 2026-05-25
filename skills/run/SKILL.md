---
name: run
description: End-to-end Bayesian statistical modeling workflow — EDA, model design, fitting, validation, and reporting via orchestrated subagents. Use when building probabilistic models with Stan and ArviZ.
disable-model-invocation: true
argument-hint: [data path or analysis goal]
---

# Bayesian Workflow

## Your task

$ARGUMENTS

If no dataset or analysis goal is provided above, look for data files (CSV, JSON, Parquet) in `data/`, `analysis/data/`, or the working directory and proceed with the most relevant one. If the goal is unspecified, synthesize one from the data and state it explicitly before starting.

## Objective

The final deliverable must be a Bayesian model: specify priors, perform posterior inference, and evaluate via posterior predictive checks. Non-Bayesian methods may be explored as baselines/context but must not be selected or reported as the solution.

Core principles:
- Start from generative stories: think data-generating process, not just prediction
- Specify priors explicitly and validate via prior predictive checks
- Use full posterior inference (not MLE/MAP)
- Validate models with posterior predictive checks and parameter recovery checks
- Check diagnostics: R-hat, ESS, divergences, trace plots
- Compare models via predictive performance (LOO, WAIC)
- Consider hierarchical structures when data has grouping/repeated measures
- Flag computational issues (identifiability, convergence, misspecification) when relevant

## Communication

Your outputs serve two purposes:

Terminal output:
- Keep users and developers informed of progress in real-time
- Report what you're doing and key decisions as they happen
- Be concise but informative

Written artifacts (reports, logs):
- These are the primary deliverables that users will read retrospectively
- Invoke the `artifact-guidelines` skill to get the full guidelines

## Persistent Log

Use TaskCreate/TaskUpdate for real-time task tracking (ephemeral, current session). Separately, maintain `log.md` as a lab notebook — a chronological, honest record of what happened, what surprised you, and what you learned. Write entries as you go, not as a polished retrospective.

**Append-only**: never rewrite or delete past entries to make the process look cleaner. Mistakes and dead ends are part of the record.

### What to record

**Failures and dead ends** — with enough detail to learn from. Record the actual error or symptom, what you tried, and the outcome. Summarize tracebacks; do not paste raw error dumps.
- Bad: "Exp 3 recovery check failed, moved to Exp 4"
- Good: "Exp 3 recovery: KeyError on '5%' column (CmdStanPy quantile labels). Fixed, but beta_temp bias 0.4σ. Skipped; Exp 4 recovered clean."

**Quantitative observations** — not just PASS/FAIL. After fits: wall time, divergences, treedepth, ESS minimums. After PPCs: coverage, LOO-PIT summary, residual patterns.
- Bad: "Prior predictive check passed"
- Good: "Prior PPC: 4% negative draws, prior 95% CI for mu [12, 340] vs observed [45, 280]. Reasonable."

**Surprises and intermediate observations** — things you didn't expect. These are often more valuable than conclusions.
- "sigma_group piling up near zero — day RE may not be needed"
- "EDA suggested AR(1) but day-level RE absorbed most autocorrelation — didn't expect that"

**Cross-references** — link to files so the trail is followable.
- "See `experiments/exp2/critique/critique_report.md` for full diagnostics"

**Phase transitions and key decisions** — why you chose paths, skipped models, or revised approaches.

**Question status** — track what you're learning about each structural question. When evidence accumulates (a model passes or fails, a critique reveals something), note what it means for the question. When a question is resolved — either answered or shown to be unresolvable with the available data — record the answer and the evidence that settled it.
- "Q1 (day-level RE): exp_1 baseline vs exp_2 with day RE — ELPD +42±8, day RE clearly needed. Resolved: yes, day-level variation matters."
- "Q2 (weather effects): exp_3 added weather → ELPD +3±5, not distinguishable. Critique found residual seasonal pattern — new question: is it annual cycle, not weather?"

### Style

Keep entries dense — one to three lines per observation. The log is a working record, not a narrative. Log after each substantive step (fits, checks, design decisions), not just at phase boundaries.

## Tool Usage

- Proactively use the Agent tool with specialized subagents when the task matches the subagent's description
- When calling multiple tools, invoke independent tools in parallel for efficiency
- For tools with dependencies, call them sequentially - never use placeholders or guess missing parameters
- To run multiple subagents in parallel, send a single message with multiple Agent tool uses
- Use specialized file tools (Read, Edit, Write) instead of bash commands (cat, sed, echo)
- Reserve bash exclusively for system commands (git, uv)

### Parallel Subagents
Use parallel subagents to explore multiple perspectives simultaneously, particularly for EDA and model design where uncertainty is high. Each instance needs isolated workspace and files to avoid conflicts. Launch all instances at once using multiple Agent tool calls in a single message.

Setup: Prepare separate data copies if needed and assign each instance its own output directory (e.g., `eda/analyst_1/`, `eda/analyst_2/`). Give each instance a different focus area.

Execution: Typical count is 2-3 instances. If an instance fails, relaunch once; if it fails again, proceed with successful instances.

After completion: Synthesize findings from all instances and document convergent patterns (all agree) and divergent insights (unique to one).

## Task Pool for Pipeline Flow

Model development involves many experiments (model classes × variants, often 7-10+). Instead of synchronizing at each stage, experiments flow independently through the validation pipeline:

```
Experiment lifecycle:
prior → recovery → fit → ppd → critique → ✓ complete
   ↓ fail    ↓ fail    ↓ fail  ↓ fail    ↓ BROKEN
 refine (FIX) → re-enter at failed stage (or skip if budget exhausted)

Back-edges from critique:
  A  VIABLE/CONCERNS + suggestions → refiner (EXPLORE) → new variant → prior
  D  new structural question discovered → designer → new experiments → prior

Back-edges from model-selector (after all experiments terminal):
  E  CONTINUE_QUESTION → refiner (EXPLORE) → new variant → prior
  D  new structural question discovered → designer → new experiments → prior
     COVERAGE: GAPS → designer → gap experiments → prior
```

Use a **global task pool** mixing experiments at different stages:

```
Pool at any moment:
├─ "prior-predictive-checker exp_A2"    (entering pipeline)
├─ "model-fitter exp_C1"               (passed recovery)
├─ "posterior-predictive-checker exp_D1"(passed fit)
├─ "critique exp_E1"                   (passed ppd)
└─ "prior-predictive-checker exp_B1_fix1" (re-entering after refine)
```

**Task tracking**: Use `TaskCreate`/`TaskUpdate`/`TaskList` to track subagent dispatch. Two states only:
- Task exists, not completed → needs to be launched
- Task completed → done, never re-launch

**Main loop**:
1. Initialize: `TaskCreate("prior-predictive-checker {exp_id}")` for each experiment from experiment_plan
2. While any task not completed:
   a. `TaskList` to find incomplete tasks — **always check before dispatching**
   b. Launch up to 3-5 incomplete tasks as parallel `Agent` calls
   c. As each returns, `TaskUpdate(id, "completed")` and then:
      - **Pass** → `TaskCreate` for next stage
      - **Fail** → `TaskCreate("prior-predictive-checker {variant}")` after invoking `model-refiner` (FIX), or skip if refine budget (2) exhausted
      - **Critique VIABLE/CONCERNS + suggestions** → mark complete, `TaskCreate("prior-predictive-checker {variant}")` after invoking `model-refiner` (EXPLORE)
      - **Critique new question** → invoke `model-designer`, `TaskCreate` for resulting experiments
      - **Critique BROKEN** → invoke `model-refiner` (FIX), `TaskCreate("prior-predictive-checker {variant}")` or skip
3. All tasks completed → invoke `model-selector`

**Compaction safety**: After context compression, `TaskList` is the ground truth. Always check it before dispatching. If a completed task's outcome is unclear, read its report file in the canonical location to determine the next step. Never re-launch a completed task.

**Task granularity**: One task per experiment per pipeline stage — NOT coarse phase-level tasks.

```
Correct (per-experiment, per-stage):
TaskCreate("prior-predictive-checker exp_1")
TaskCreate("recovery-checker exp_1")
TaskCreate("model-fitter exp_1")
TaskCreate("posterior-predictive-checker exp_1")
TaskCreate("critique exp_1")

Wrong (phase-level):
TaskCreate("Phase 3: Model Development")  ← too coarse, no pipeline enforcement
```

**Sync points**: Only sync after all experiments reach terminal state (all tasks completed or experiments skipped). Fast experiments finish while slow ones are still being refined.

## Technical Stack

- Bayesian inference: Stan via CmdStanPy, ArviZ for diagnostics
- Package management: `uv` exclusively (never bare `python` or `pip`)
- First run: set up the Python environment (dependencies + bundled `shared_utils`) by running the `/bayesian-workflow:setup` command. Check for `./pyproject.toml` and `./shared_utils/` first — the user may have already run it.
- Scripts should be self-contained and run with `uv run`

Every accepted Bayesian model must use Stan via CmdStanPy for posterior inference with NUTS. Do not substitute MLE/MAP for full Bayesian inference, use non-PPL implementations as final models, or label bootstrap-based checks as posterior predictive checks.

## File-Based Communication and Folder Structure

Files are the only persistent communication channel between subagents and across phases. Always specify exact paths when invoking subagents: where to read inputs and where to write outputs.

### Canonical Structure
Use this structure unless the task requires deviation:

```
data/                           # source data and copies
eda/                            # Phase 1: Data Understanding
  eda_report.html                 # final synthesis (required)
  quality_summary.csv           # data quality table (required)
  univariate_summary.csv        # per-variable summary stats (required)
  analyst_1/                    # if parallel: each instance gets own folder
  analyst_2/
design/                         # Phase 2: Model Design
  designer_1/
    designer_proposal.md        # (required)
  designer_2/
    designer_proposal.md        # (required)
  experiment_plan.md            # synthesized plan (required)
experiments/                    # Phase 3: Model Development
  experiment_1/                 # one folder per model attempt
    model.stan                  # main inference model
    prior_predictive/
      prior_model.stan          # GQ-only: mirrors priors, generates y_rep
      prior_predictive_report.md  # (required)
      prior_predictive.nc       # ArviZ InferenceData (prior + prior_predictive)
      *.png, *.py
    simulation/
      simulator.stan            # GQ-only: true params as data, generates y_rep
      recovery_report.html      # (required)
      *.png, *.py
    fit/
      fit_report.md             # convergence diagnostics, assessment (required)
      posterior.nc              # ArviZ InferenceData (needed through reporting)
      thinned_draws.npz         # parameter draws only (lightweight)
      loo.json                  # LOO results: ELPD, Pareto k (needed by selector)
      *.png, *.py
    posterior_predictive/
      posterior_predictive_report.md  # (required)
      *.png, *.py
    critique/
      critique_report.md        # statistical + domain + framework (required)
      *.png, *.py
  experiment_2/
  population_assessment.md      # model-selector output (required)
final_report.md                 # Phase 4 output (required)
log.md                          # append-only workflow log
```

### Subagent Communication
Point subagents to files produced by previous subagents rather than summarizing content yourself (e.g., tell model-designer to "Read the EDA report at `eda/eda_report.html`" rather than summarizing EDA findings). Ask subagents to report what files they created so you can pass information along the chain.

## Modeling Workflow

### Phase 1: Data Understanding → `eda/`
Invoke `eda-analyst` to explore the data. For complex datasets, run 1-3 instances in parallel with different focus areas, then synthesize results into `eda/eda_report.html`.

### Phase 2: Model Design → `design/`

**Step 1: Define analysis purpose, domain context, and structural questions.** Read the EDA report's Competing Structural Hypotheses, Variance Decomposition, Residual Analysis, and Scientific Domain sections.

**1a. Analysis purpose.** Determine the goal type based on the user's prompt and the data's nature:
- **Descriptive** (default for minimal prompts): characterize the data-generating process with honest uncertainty.
- **Inferential**: estimate a specific causal or conditional effect. Prioritize unconfounded estimation of target parameters; do not add flexible structures that absorb the estimand's signal.
- **Predictive**: maximize out-of-sample performance; parameter interpretability is secondary.

If the user prompt lacks a specific question, **assume loudly**: synthesize a purpose based on the dataset's nature and state it explicitly. A sharp answer to an assumed question is better than a generic answer to no question.

Define 1-3 **key quantities of interest** and state what **adequate** means — when is the model good enough to stop?

**1b. Validation strategy.** Define how models will be evaluated, accounting for the data's dependence structure. Standard observation-level LOO is only appropriate for i.i.d. data — for grouped data it interpolates within known groups, and for temporal data it overstates future predictive performance. State the appropriate hold-out scheme.

**1c. Domain context.** Identify the scientific domain and its canonical modeling frameworks. Do not default to generic GLMs when the domain has mechanistic structure — use the domain's standard response model, parameterization, and baseline components.

If the domain is not recognizable, state "No strong domain conventions identified" and proceed with empirical-first design.

**1d. Structural questions.** Extract 2-3 contrastive structural questions — each should pit two explanations of the data-generating process against each other, framed in terms of the key quantities of interest and domain theory where possible.

Write steps 1a-1d as the opening sections of `design/experiment_plan.md`. All downstream agents read this.

**Step 2: Define a domain-aware shared baseline.** Construct a baseline that implements the domain's canonical theory, reconciled with EDA findings. If no domain conventions were identified, fall back to the simplest model that captures the dominant EDA structure. All designers extend from this baseline.

**Step 3: Assign questions to designers.** Run 2-3 `model-designer` instances in parallel. Give each their assigned question, the shared baseline, the other designers' questions, and their output directory. Encourage designers to consider structurally different model families (not just parametric extensions of the baseline) if they better match the data-generating process. Each designer produces a resolution sequence that answers their question.

**Step 4: Synthesize.** Read all designer proposals and produce the final `design/experiment_plan.md`. De-duplicate overlapping models, add cross-cutting experiments where designer questions interact, order by information value, and set total experiment count (typically 6-10).

### Phase 3: Model Development and Selection → `experiments/`

Use the task pool (see "Task Pool for Pipeline Flow") to validate all experiments from the experiment plan. Each experiment flows through 5 stages: `prior-predictive-checker` → `recovery-checker` → `model-fitter` → `posterior-predictive-checker` → `critique`.

The `critique` agent performs statistical assessment, domain assessment, and framework questioning in a single pass.

**Failure handling**:
- Any stage fails → invoke `model-refiner` once, re-enter at failed stage
- Refine fails → skip experiment
- Special case: If a structural question's baseline variant fails pre-fit (prior or recovery), skip all experiments for that question after one refine attempt
- **Global budget**: Each experiment has a maximum of TWO `model-refiner` invocations across its entire lifecycle (all stages combined). If it fails a third time at any stage, mark it skipped.

**Critique-driven iteration (REQUIRED)**:
When `critique` returns VIABLE or CONCERNS with improvement suggestions, you MUST:
1. Invoke `model-refiner` in EXPLORE mode with the specific suggestions (prioritize PRIORITY 1 concerns — especially framework concerns)
2. Create a modified variant (e.g., `exp_1_v2`, `exp_1_robust`)
3. Add the new variant to the task pool for validation
4. Compare the modified variant against its parent via LOO/ELPD
5. If the modification improved the model, critique it again and repeat
6. Stop iterating when: modifications no longer improve ELPD, or suggestions become unreasonable/impractical

The goal is to **iterate until reasonable modifications stop helping**, not just validate pre-designed experiments. Each structural question should have multiple iterations showing progressive refinement or evidence that simpler versions suffice.

Do NOT skip directly to model selection after initial experiments. Do NOT stop after one iteration if the modification helped and critique suggests further improvements.

**Discovery-driven questions**:
Critique and selection are not just quality gates — they are sources of new hypotheses. When critique reveals something genuinely surprising (unexpected residual structure, a parameter collapsing to zero, a domain mechanism that the original questions didn't anticipate, or unused data that could support a better framework), this may warrant a **new structural question** rather than a tactical refinement of the existing model.

Distinguish between:
- **Refinement suggestion** → model-refiner creates a variant within the current question
- **New structural question** → model-designer designs new experiments with the current best model as baseline

When you identify a new question from critique or selection insights:
1. Invoke `model-designer` with the new question and the **current best model** as `baseline_spec` (not the original Phase 2 baseline — build on what you've learned)
2. Add the resulting experiments to the task pool
3. The new experiments flow through the same validation pipeline as the original ones

This is the scientific process: hypothesize → test → observe → generate new hypotheses. A finite dataset has finite structure, so the questions will converge naturally. Do not artificially limit discovery — if the agent keeps finding genuine structure, that is valuable work.

**When all experiments terminal** → invoke `model-selector` with experiments that completed critique with VIABLE or CONCERNS verdict (exclude BROKEN — they were sent to refinement or skipped):
- Compares validated experiments using the comparison method appropriate to the data structure
- **CONTINUE_QUESTION**: `model-refiner` generates new variants → add to task pool
- **SWITCH_QUESTION**: This question is resolved; move focus to next question
- **ADEQUATE/EXHAUSTED**: The selector's assessment includes a **Coverage Audit** section

The selector may also report **new structural questions** discovered from model comparison (unexpected patterns, discriminating features) alongside any of the above decisions. If present, invoke `model-designer` with each new question, using the current best model as `baseline_spec`.

**Coverage audit**: When the `model-selector` subagent returns ADEQUATE or EXHAUSTED, read its `COVERAGE:` section from `experiments/population_assessment.md`. If `COVERAGE: GAPS`, invoke `model-designer` for each gap (using the current best model as `baseline_spec`) and add the resulting experiments to the task pool. If `COVERAGE: COMPLETE`, proceed to reporting.

### Phase 4: Reporting → `final_report.md`
Invoke `report-writer` with the selected model's experiment directory (`selected_model_dir`). The `report-writer` subagent will compute practical contrasts and write the final report.
