---
name: bayesian-model-selection
description: Comparing model populations via ELPD, decision rules for selection vs stacking, and metric validity
---

# Bayesian Model Selection

Operational guide for comparing a population of validated Bayesian models. Covers `az.compare()` interpretation, ELPD-based decision rules, and when to stack vs pick a winner.

For single-model diagnostics (LOO-PIT, Pareto k), see `bayesian-model-diagnostics`. For MCMC sampler health, see `convergence-diagnostics`.

## Metric Validity Precondition

**Check BEFORE trusting `az.compare()` rankings:**

Do not trust ELPD rankings if the underlying LOO estimates were computed on dependent data (time-series, spatial, grouped) using standard `az.loo()`. Standard LOO assumes conditional independence — on dependent data it will overstate predictive performance and can flip model rankings.

| Data structure | ELPD rankings valid? | Action |
|---|---|---|
| **i.i.d.** | Yes | Proceed with `az.compare()` |
| **Time-series** | Only if LOO used LFO-CV or rolling-origin | If standard LOO was used, demand rolling forecast metrics before declaring a winner |
| **Grouped** | Only if LOO matches prediction target | If generalizing to new groups, LOO must leave out entire groups |

### Implementation Note

If you need rolling CV, Diebold-Mariano tests, grouped LOO, or other non-standard comparison methods, check `shared_utils` first — it may already have an implementation. Do not write custom evaluation loops from scratch if a shared utility exists.

## ELPD Comparison Rules

Run `az.compare()` on all validated models. This produces ELPD differences (Δ ELPD) with standard errors (SE) and stacking weights.

### Rule 1: Clear Winner (ΔELPD > 4×SE)

The top model's ELPD exceeds the second-best by more than 4× the SE of the difference.

- **Action:** Pick the winner. This is strong evidence of superior predictive performance.
- **Report:** "Model X is the clear winner (ΔELPD = 15.2, SE = 3.1). Recommend proceeding with Model X."

### Rule 2: Likely Winner (2×SE < ΔELPD < 4×SE)

Moderate evidence favoring the top model.

- **Action:** Prefer the top model, but note the uncertainty. If the runner-up is substantially simpler, consider it.
- **Report:** "Model X is favored (ΔELPD = 7.4, SE = 2.8) but the difference is moderate. Model Y is simpler and within striking distance."

### Rule 3: Indistinguishable (ΔELPD < 2×SE)

The top models overlap — the nominal ranking is not meaningful.

- **Sub-rule 3A (Occam's razor):** If one model is substantially simpler (fewer parameters, no unnecessary hierarchical structure), prefer it. Equal predictive performance with less complexity is better.
- **Sub-rule 3B (Stacking):** If `az.compare()` assigns significant weight (>0.15) to multiple models, they capture different aspects of the data. Recommend stacking.
- **Report:** "Models X and Y are statistically indistinguishable (ΔELPD = 1.2, SE = 2.4). Stacking weights: X = 0.6, Y = 0.4. Recommend stacked ensemble."

## Stacking Weight Interpretation

`az.compare()` produces stacking weights that minimize leave-one-out predictive loss. These are more useful than raw ELPD rankings when models are close.

| Weight pattern | Meaning | Action |
|---|---|---|
| One model has weight ≈ 1.0 | Single model dominates predictive performance | Pick the winner — stacking offers no benefit |
| 2-3 models share weight (e.g., 0.5/0.3/0.2) | Models capture complementary data features | Recommend stacked ensemble. Note which aspects each model captures |
| Weights spread thinly across many models | No model stands out; high model uncertainty | Consider whether models are all slight variants (→ simplify the candidate set) or structurally different (→ genuine ensemble value) |

Prefer stacking over Bayesian Model Averaging (BMA). BMA assumes one true model exists and is prior-sensitive. Stacking is robust to all models being wrong.

## Complexity Ceiling Detection

Track the improvement trajectory across model variants within a structural question:

| Pattern | Signal | Recommendation |
|---|---|---|
| Each variant improves ELPD over its predecessor | Question has room to grow | CONTINUE_QUESTION — try next suggested refinement |
| Recent variants show diminishing ELPD gains (<1 SE improvement) | Approaching ceiling | One more attempt, then SWITCH_QUESTION or declare ADEQUATE |
| Added complexity *hurts* ELPD (more parameters, worse score) | Overfitting or misspecified extension | Revert to simpler variant. SWITCH_QUESTION if baseline was already the best |
| All classes explored, best models identified, no variant improves | Modeling exhausted | EXHAUSTED — accept best model(s) and proceed to reporting |

## Pareto k in Population Context

Before comparing models, verify that each model's LOO is trustworthy:

- If a model has >5% of observations with Pareto k > 0.7, its ELPD is unreliable. Either refit with `az.reloo()` or exclude it from the comparison and note why.
- If *all* models have high Pareto k, the comparison is unreliable. Flag this and recommend k-fold CV for the entire population.

## Output Checklist

When writing `experiments/population_assessment.md`, include:

1. ELPD ranking table (all validated models, with ΔELPD ± SE). **Always report both the ELPD difference AND its standard error** — an ELPD difference without SE is uninterpretable. Also report p_loo and number of high Pareto k observations per model.
2. Stacking weights from `az.compare()`
3. `az.plot_compare()` visualization
4. Best model per structural question
5. Improvement trajectory (did variants help?)
6. Strategic recommendation: CONTINUE_QUESTION / SWITCH_QUESTION / ADEQUATE / EXHAUSTED
7. If ADEQUATE/EXHAUSTED: whether to pick a single winner or stack, with justification
8. `az.plot_elpd()` for pointwise ELPD differences — shows WHICH observations drive model comparison results, not just aggregate scores. Critical for diagnosing whether one model is uniformly better or only better on specific subgroups/outliers
