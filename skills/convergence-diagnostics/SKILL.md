---
name: convergence-diagnostics
description: MCMC convergence diagnostics using CmdStanPy and ArviZ
user-invocable: false
---

# Convergence Diagnostics

Use this skill when checking MCMC convergence after fitting Stan models. Convergence means chains mixed and explored the same target, and you have enough effective draws.

## CmdStanPy Diagnostics

After fitting with CmdStanPy, run:
- `fit.summary()`: Returns DataFrame with `R_hat`, `ESS_bulk`, `ESS_tail`, `MCSE` per parameter
  - **Note**: Recent CmdStanPy versions use `ESS_bulk` and `ESS_tail` (not `N_Eff` or `N_eff`)
  - Column names are UPPERCASE: `R_hat` not `r_hat`
- `fit.diagnose()`: Checks for divergences, max treedepth, low E-BFMI, low ESS, high R-hat
  - **Warning**: Can OOM on large datasets (N > 10K). Use `shared_utils.check_convergence()` instead.

If `diagnose()` reports no problems, you still need visual checks via ArviZ.

## ArviZ Workflow

Convert to InferenceData:
```python
# IMPORTANT: Use consistent naming - y_obs for observed, y_rep for posterior predictive
idata = az.from_cmdstanpy(
    fit,
    log_likelihood="log_lik",           # must exist in generated quantities
    posterior_predictive=["y_rep"],      # must exist in generated quantities
    observed_data={"y": y_obs}           # provides observed data group
)
```

**Common ArviZ conversion errors:**
- `KeyError: 'y'` or `KeyError: 'y_rep'`: Variable not in Stan generated quantities - check naming
- `KeyError: 'prior'`: Prior group requires prior predictive samples (not needed for most workflows)
- `TypeError: unhashable type 'ndarray'`: ArviZ conversion fails with arrays in sets - use `list()` wrapper
- Use `az.from_cmdstanpy()` for ArviZ conversion

Run numerical diagnostics:
- `az.rhat(idata)`: Rank-normalized split R-hat (lowercase `r_hat` in output)
- `az.ess(idata)`: Bulk and tail effective sample size (lowercase `ess_bulk`, `ess_tail`)
- `az.bfmi(idata)`: Bayesian fraction of missing information
- `az.mcse(idata)`: Monte Carlo standard error
- `az.summary(idata)`: All diagnostics in one table
  - **Note**: ArviZ uses lowercase column names (`r_hat`, `ess_bulk`), CmdStanPy uses uppercase

## Thresholds

Must achieve:
- **R̂ < 1.01** (all parameters) - measures chain agreement
- **ESS bulk and tail ≥ 400** per parameter - enough effective draws
- **BFMI ≥ 0.3** per chain - adequate energy exploration
- **MCSE << posterior SD** - Monte Carlo error small relative to uncertainty
- **No divergent transitions** after warmup

## Visual Diagnostics

**Chain mixing and stationarity:**
- `az.plot_trace()`: Should show "fat fuzzy caterpillars", no trends or stuck chains. Divergences shown as vertical lines.
- `az.plot_rank()`: Rank histograms should be uniform and similar across chains. U-shapes or skew indicate poor mixing.

**Autocorrelation and ESS:**
- `az.plot_autocorr()`: Slow decay indicates high correlation and low ESS
- `az.plot_ess(kind="evolution")`: ESS growth over draws - should keep climbing
- `az.plot_ess(kind="local")`: ESS in local windows/quantiles - checks tail exploration

**HMC-specific pathologies:**
- `az.plot_energy()`: Overlays energy transitions vs marginal energy. Low BFMI shows mismatch.
- `az.plot_pair(divergences=True)`: Localizes divergences in parameter space (funnels, tight correlations). For hierarchical models: plot each group-level parameter vs `log(population_scale)` with divergent transitions highlighted. Divergences near small scale = centered funnel (use non-centered). Divergences near large scale = inverted funnel (use centered)
- `az.plot_parallel()`: Parallel coordinates showing divergent vs non-divergent draws

## Common Issues

**Convergence problems:**
- **Divergences + low BFMI**: Geometry problems (funnels, stiff regions). Reparameterize or increase adapt_delta to 0.95-0.98.
- **High R̂, good visuals**: Chains haven't run long enough. Extend iterations.
- **Low ESS, good R̂**: High autocorrelation. Reparameterize (non-centered) or run longer.
- **Max treedepth warnings**: Strong correlations. Reparameterize or simplify model.
- **Multimodality in plot_posterior**: Identification problem or multiple modes.

**Data/API issues:**
- **KeyError on ESS_bulk/ESS_tail**: Using old code expecting `N_Eff` - update to `ESS_bulk`.
- **AttributeError 'no prior group'**: Don't reference `idata.prior` unless prior predictive was generated.
- **Missing y/y_rep variables**: Inconsistent naming in Stan vs Python - standardize on `y_obs`/`y_rep`.
- **ValueError during summary**: Non-numeric columns passed to stats - filter with `df.select_dtypes(include="number")`.

## Convergence Without Identifiability

A model can have R-hat < 1.01, zero divergences, and adequate ESS while being structurally non-identified. Convergence diagnostics only verify the sampler explored its target — they do not verify the target is well-posed.

Signs of non-identifiability despite clean convergence:
- Pairs plots show ridge, surface, or circular structures (parameters trade off against each other)
- Posterior SDs do not shrink proportional to 1/√N when data size increases
- Parameter pairs with |correlation| > 0.95
- Mixture models: R-hat > 10 for component parameters without any divergences (label-switching). Fix with ordering constraints, not longer chains.

If suspected: classify the degeneracy (additive redundancy `a+b=const`, multiplicative `a×b=const`, label symmetry) and reparameterize to identified quantities (anchor one reference level, use contrasts instead of absolute effects, apply ordering constraints for mixture components).

Remember: You never prove convergence, only build a strong circumstantial case. The sampler tells you about your model - listen to it.
