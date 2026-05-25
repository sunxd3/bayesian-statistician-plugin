# Single-Draw Fake-Data Simulation

One true-param set, simulate once, refit, check recovery. Cheap pre-fit gate. Catches obvious model bugs, Stan-program errors, and gross non-identifiability without the cost of full Simulation-Based Calibration.

## Procedure

### 1. Choose true parameter values

Pick **one** realistic set of parameter values (optionally a second set if the model has known identifiability risks). Informed by domain knowledge and EDA summaries. Avoid corner cases — the goal is "can the model recover *plausible* truth," not "can it recover edge cases."

### 2. Write `simulator.stan`

A generated-quantities-only Stan program at `<output_dir>/simulator.stan`. Takes the true parameter values as `data{}` input and generates synthetic `y_rep`. No `parameters` block, no `model` block.

The transformed-parameter computation and `_rng` calls **must be a line-by-line mirror** of the corresponding blocks in `model.stan`. Any divergence between simulator and model invalidates the check.

See the `stan` skill for full GQ-only patterns and pitfalls.

### 3. Generate synthetic data in Stan

```python
from shared_utils import compile_model, fit_model, cleanup_csv_files

# Pass true parameters as data
true_params = {"alpha_true": 2.5, "sigma_true": 1.0}
sim_data = {**stan_data, **true_params}

simulator = compile_model(sim_dir / "simulator.stan")
sim_fit = fit_model(simulator, sim_data, fixed_param=True,
                    iter_warmup=0, adapt_engaged=False, iter_sampling=1)
y_synth = sim_fit.stan_variable("y_rep")
cleanup_csv_files(sim_fit)
```

### 4. Fit `model.stan` to the synthetic data

```python
from shared_utils import compile_model, fit_and_summarize

model = compile_model(experiment_dir / "model.stan")
synth_stan_data = {**stan_data, "y_obs": y_synth.flatten()}
result = fit_and_summarize(model, synth_stan_data, model_name="recovery",
                           save_dir=sim_dir)
```

Do NOT use raw `model.sample()` — progress bars crash the agent transcript, and raw calls skip CSV cleanup.

### 5. Check recovery

Compare the fitted posterior to the truth:

- **Recovery**: posterior means/medians within a few standard errors of the true values
- **Coverage**: posterior credible intervals contain the true values
- **Convergence**: MCMC converges on the synthetic data without major issues (R-hat, ESS, divergences)
- **Identifiability**: no wild parameter uncertainty or correlations that prevent recovery
- **Computational stability**: fits complete without errors

## Visualization

- **Scatter**: posterior mean (y) vs true value (x), one point per parameter. Should track near the identity line with mild shrinkage.
- **Interval plot**: for each parameter, plot the posterior credible interval with the true value overlaid as a point or vertical line.

Look for:
- Catastrophic failures (flat line, no learning of the truth)
- Wild scatter (non-identifiability)
- Convergence issues visible in trace plots or pair plots

See `references/decision.md` for full PASS/FAIL criteria and failure-mode triage.
