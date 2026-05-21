---
name: visual-predictive-checks
description: Guidelines for visual predictive checks following Säilynoja et al. recommendations using ArviZ
---

# Visual Predictive Checks

Use this skill when running prior or posterior predictive checks to validate Bayesian models. These checks compare simulated data from the model to observed data (or plausible ranges for prior predictive checks).

## ArviZ Workflow

1. Fit model with CmdStanPy, generating predictive quantities in `generated quantities` block
   - **CRITICAL**: Use consistent naming: `y_rep` for posterior predictive (not `y_pred`, `y_sim`, `y`)
   - For observed data: use `y_obs` (not just `y`)
   - This prevents KeyError issues in ArviZ conversion
2. Convert to ArviZ InferenceData using `az.from_cmdstanpy`
   ```python
   idata = az.from_cmdstanpy(
       fit,
       posterior_predictive=["y_rep"],  # must match Stan variable name
       observed_data={"y": y_obs}       # ArviZ expects "y" key
   )
   ```
3. Create visual checks using ArviZ plot functions

## Visual Checks by Data Type

### Continuous Data
- **Distribution**: `plot_ppc_dist` with `kind="ecdf"` and `kind="kde"`
- **PIT ECDF**: `plot_ppc_pit` - shows calibration with simultaneous bands
- **Coverage**: `plot_ppc_pit(coverage=True)` - equal-tailed interval coverage
- **Summary statistics**: `plot_ppc_tstat` for median, MAD, IQR combined with `combine_plots`
- **LOO-PIT**: `plot_loo_pit` - avoids double-dipping by using leave-one-out

### Count Data
- **Rootogram**: `plot_ppc_rootogram` - emphasizes discreteness and dispersion
- **Histogram**: `plot_ppc_dist(kind="hist")`
- **PIT ECDF** and **coverage**: Same as continuous

### Binary/Categorical/Ordinal Data
- **Calibration**: `plot_ppc_pava` - PAV-adjusted calibration curves
- **Intervals**: `plot_ppc_interval` - posterior predictive intervals with observed overlay
- **PIT ECDF** and **coverage**: Same as continuous

### Censored/Survival Data
- **Survival curves**: `plot_ppc_censored` - Kaplan-Meier style PPC
- **PIT ECDF** and **coverage**: Same as continuous

## Conditional and Residual Checks

Marginal PPCs (overall distribution checks) can pass while the model is seriously misspecified at the covariate level. Always supplement marginal checks with:

**Conditional PPCs:** Stratify posterior predictive checks by key covariates identified in EDA.
- Discrete covariates: compute posterior predictive mean/proportion within each level and compare to observed
- Continuous covariates: bin into 5-10 intervals and check whether posterior predictive summaries in each bin cover the observed values
- Grouped/hierarchical data: generate per-group PPCs in addition to overall — outlier groups or groups with poor coverage suggest inadequate population model

**Residual panels:** For every posterior retrodictive comparison, generate BOTH the overlay plot (predictive intervals over data) AND a residual plot (`y_rep - y_obs`). Residual plots magnify systematic deviations that are invisible in overlays. Bin residuals by time, group, or predictor to reveal structure.

**Location-function retrodiction:** For regression-type models, plot the posterior distribution of the fitted function f(x; θ) (spaghetti lines or quantile ribbons) overlaid on observed data, WITHOUT observation noise. This isolates systematic misfit from noise absorption. If the full PPC passes but the location-function check shows systematic bias, the model's σ is absorbing structural error — the model retrodicts for the wrong reasons.

## Key Principles

Use multiple complementary views rather than relying on a single plot. For example, for continuous outcomes, combine ECDF (shows full distribution) with PIT ECDF (shows calibration) and t-stat PPCs (shows specific features like central tendency and spread).

LOO-PIT is preferred over regular PIT for posterior checks as it approximates leave-one-out predictive distribution and avoids overfitting concerns. For interpreting LOO-PIT and PPC patterns (shape-to-diagnosis mappings), see `bayesian-model-diagnostics`.

Name plots descriptively: `prior_predictive_ecdf.png`, `loo_pit_calibration.png`, `posterior_rootogram.png`.

## NumPy 2.x Compatibility

**CRITICAL**: NumPy 2.x removed `np.trapz`. Use `scipy.integrate.trapezoid` instead:

```python
# ❌ WRONG - fails on NumPy 2.x
from numpy import trapz
prob = trapz(density, x)

# ✓ CORRECT - works on all versions
from scipy.integrate import trapezoid
prob = trapezoid(density, x)
```

This applies to any posterior predictive density (PPD) calculations.

## Common Issues

**Variable naming errors:**
- `KeyError: 'y_rep'`: Stan generated quantities doesn't include `y_rep` - check your Stan code
- `KeyError: 'y'`: No observed_data provided to `az.from_cmdstanpy` - add `observed_data={"y": y_obs}`
- Inconsistent naming across files causes cascading errors - stick to `y_obs`/`y_rep` standard

**NumPy/SciPy API issues:**
- `AttributeError: 'trapz' not found`: Using NumPy 2.x - switch to `scipy.integrate.trapezoid`
- Both functions have identical signatures: `trapezoid(y, x)` or `trapezoid(y, dx=dx)`
