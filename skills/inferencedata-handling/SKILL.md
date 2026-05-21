---
name: inferencedata-handling
description: Proper ArviZ InferenceData creation and validation from CmdStanPy
user-invocable: false
---

# InferenceData Handling

Use this skill when saving MCMC results to InferenceData format. Incorrect conversion is a common source of downstream failures.

## CmdStanPy to ArviZ Conversion

**Never use bare `az.from_cmdstanpy(fit)`** - it puts everything in the `posterior` group.

### Correct Pattern

```python
import arviz as az

idata = az.from_cmdstanpy(
    fit,
    posterior_predictive=["y_rep", "y1_rep", "y2_rep"],  # Variables ending in _rep
    log_likelihood="log_lik",                            # For LOO/WAIC
    observed_data={"y": y_obs},                          # Original data
    coords=coords,                                        # Dimension labels
    dims=dims,                                            # Variable dimensions
)
```

### Variable Naming Conventions

| Stan variable | InferenceData group | Notes |
|---------------|---------------------|-------|
| `*_rep` | `posterior_predictive` | Replicated data for PPC |
| `log_lik` | `log_likelihood` | Per-observation log-likelihood for LOO |
| Parameters | `posterior` | Default location |
| `*_prior` | `prior` | Prior predictive (if sampled) |

### Case Sensitivity

Stan lowercases all variable names internally:
- `Y1_rep` in Stan → `y1_rep` in CmdStanPy output
- Always use lowercase when referencing in Python

## Validation Checklist

**Before saving `posterior.nc`, verify:**

```python
def validate_idata(idata, expected_pp_vars=None):
    """Validate InferenceData has required groups and variables."""
    errors = []

    # Check posterior group exists
    if "posterior" not in idata.groups():
        errors.append("Missing 'posterior' group")

    # Check posterior_predictive if expected
    if expected_pp_vars:
        if "posterior_predictive" not in idata.groups():
            errors.append("Missing 'posterior_predictive' group")
        else:
            for var in expected_pp_vars:
                if var not in idata.posterior_predictive:
                    errors.append(f"Missing '{var}' in posterior_predictive")

    # Check log_likelihood for LOO
    if "log_likelihood" not in idata.groups():
        errors.append("Missing 'log_likelihood' group (needed for LOO)")

    if errors:
        raise ValueError(f"InferenceData validation failed: {errors}")

    return True

# Usage
validate_idata(idata, expected_pp_vars=["y_rep"])
idata.to_netcdf("posterior.nc")
```

## Common Failures

### 1. KeyError in PPC checker
```
KeyError: 'y_rep'
```
**Cause:** `posterior_predictive=` not specified in `az.from_cmdstanpy()`
**Fix:** Explicitly list all `*_rep` variables

### 2. LOO fails with missing log_likelihood
```
KeyError: 'log_lik'
```
**Cause:** `log_likelihood=` not specified
**Fix:** Add `log_likelihood="log_lik"` (must match Stan variable name)

### 3. Dimension mismatch in plots
**Cause:** Missing `coords` and `dims`
**Fix:** Provide coordinate labels:
```python
coords = {"obs": np.arange(N), "group": group_names}
dims = {"y_rep": ["obs"], "alpha": ["group"]}
```

### 4. Case mismatch
```
KeyError: 'Y_rep'  # But Stan has y_rep (lowercase)
```
**Cause:** Stan lowercases everything
**Fix:** Use lowercase in Python code

## Full Example

```python
import arviz as az
import numpy as np

# After fitting
fit = model.sample(data=stan_data, ...)

# Identify generated quantities from Stan model
# generated quantities {
#   vector[N] y_rep;
#   vector[N] log_lik;
# }

# Convert with explicit groups
idata = az.from_cmdstanpy(
    fit,
    posterior_predictive=["y_rep"],
    log_likelihood="log_lik",
    observed_data={"y": y_obs, "x": x_obs},
    coords={"obs_id": np.arange(len(y_obs))},
    dims={"y_rep": ["obs_id"], "log_lik": ["obs_id"]},
)

# Validate before saving
assert "posterior_predictive" in idata.groups()
assert "y_rep" in idata.posterior_predictive
assert "log_likelihood" in idata.groups()

# Save
idata.to_netcdf("posterior.nc")
print(f"Saved: {idata.groups()}")
```

## Loading and Verification

```python
# Load saved file
idata = az.from_netcdf("posterior.nc")

# Verify structure
print("Groups:", idata.groups())
print("Posterior vars:", list(idata.posterior.data_vars))
print("PP vars:", list(idata.posterior_predictive.data_vars))
print("Log-lik vars:", list(idata.log_likelihood.data_vars))
```
