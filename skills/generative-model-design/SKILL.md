---
name: generative-model-design
description: Required design decisions for complete generative model specifications
---

# Generative Model Design

Your specification is incomplete until you have explicitly addressed every section below. Each section is a required decision, not a lesson — execute these structural commitments.

## 1. The Measurement Story

Before choosing any distribution, commit to the measurement story. Write one sentence:

> "For each [unit], there is a latent [quantity]. The observed [variable] is [relationship] corrupted by [noise source], which [scales how]."

This forces you to separate the **process model** (noiseless latent truth) from the **observation model** (how instruments, sampling, and recording produce the data you see). Most likelihood mistakes come from conflating these two.

Check for observation process artifacts: Is there censoring (measurement caps out)? Truncation (some values never recorded)? Rounding or heaping? Selection bias (only certain units observed)? These are likelihood features, not preprocessing details.

## 2. Observation Unit & Independence

State explicitly:
- **What is one row of data?** (e.g., person-day, sensor-reading, aggregated daily count). Do not aggregate data to fit a simpler likelihood; model at the measured resolution. Use hierarchy to make inferences at higher levels.
- **Can rows be permuted without changing meaning?** If yes, conditional independence given parameters is plausible. If no (time ordering, spatial adjacency, nesting), specify the dependence structure explicitly.

**Evaluation implications:** The data structure determines which validation tools are reliable downstream. For i.i.d. data, standard LOO and ELPD comparisons work. For temporal or spatial dependence, standard LOO overstates predictive performance — specify appropriate validation (rolling-origin, leave-future-out, leave-group-out) in your falsification criteria. See `bayesian-model-diagnostics` for data-structure preconditions.

## 3. Likelihood Decisions

Justify these three choices:
- **Support:** The likelihood must not assign probability to impossible values. Match the distribution family to the data's boundaries (counts cannot be Normal; positive quantities need positive-support distributions).
- **Noise geometry:** Is noise additive on the original scale (Normal family) or multiplicative / proportional to the mean (LogNormal/Gamma family)? Signal from EDA: if coefficient of variation is roughly stable, noise is multiplicative.
- **Dispersion:** Is variance constant, or does it vary with covariates or groups? If the EDA shows structured variance (fan shapes, group heterogeneity), model dispersion explicitly — this is often a better fix than switching to heavy-tailed distributions.
- **Specialized zero/boundary processes:** Use **Hurdle** when zeros come from a single binary decision (one process), but **Zero-Inflated** when zeros mix structural absence and sampling zeros (two processes). Use **Censored** (`censored_*` in Stan) when out-of-bounds values are recorded at the threshold (fixed N), but **Truncated** (`T[,]` in Stan) when they are simply unobserved (variable N). Getting this wrong passes recovery checks (same wrong model generates and fits) and only fails at PPC on real data — wasting both a recovery run and a full fit.

## 4. Pooling & Hierarchy

If the data has grouped observations, state the information-sharing structure:
- Identify the grouping factor(s).
- Which parameters are completely pooled (one global value), unpooled (independent per group), or partially pooled (hierarchical)? Are you pooling intercepts, slopes, or both?
- Justify *why* groups share information (e.g., "stations in the same city share unobserved demand drivers"). Do not default to unpooled estimates for sparse groups.

## 5. Prior Implications

Do not just list prior distributions — state their implications on the observable scale. For parameters on transformed scales (logit, log), translate the prior to the natural scale and verify the implied range covers plausible values without extending to physical absurdities.

For hierarchical models, explicitly define the hyperprior on the group-level standard deviation. It must be strictly positive and control the degree of shrinkage.

**Containment prior calibration:** For any parameter with plausible domain bounds [L, U], calibrate the prior so ~98% of mass falls inside. Quick formula for Normal prior: σ ≈ (U - L) / 4.64. For positive parameters, use lognormal or gamma tuned via quantile matching to the containment targets.

After setting priors, run a **prior pushforward check**: draw parameters from the prior, compute derived/transformed quantities (probabilities, rates, observable-scale predictions), and verify they don't pile up at boundaries (0 or 1 for probabilities, 0 or ∞ for scales). If they do, iteratively tighten the prior until the pushforward is sensible. This catches geometry problems that direct prior checks miss — a prior that looks reasonable in parameter space can produce absurd predictions.

**Prior anti-patterns that cause geometry problems (not caught by prior predictive checks):**
- Never use `inv_gamma` for variance/scale hyperpriors — it creates artificial lower bounds on group-level variation and funnel geometry. Prefer `exponential`, `normal<lower=0>`, or `student_t(3, 0, s)<lower=0>`.
- For correlation matrices, use `lkj_corr_cholesky(eta)` with `eta >= 2` to regularize toward identity. `eta = 1` is uniform over correlation matrices (often too diffuse); `eta < 1` favors extreme correlations.

## 6. Identifiability Risks

Flag expected computational problems for downstream agents:
- Are there parameter combinations that produce indistinguishable data at your sample size? Note what the recovery checker should watch for.
- Does the hierarchy create funnel geometry (sparse groups)? Note parameterization preference (centered vs non-centered).
- Can coefficients diverge (separation in logistic models with rare events)? Regularizing priors are mandatory.
- **Redundant intercepts:** Never include both a global intercept and unconstrained group-level intercepts (e.g., `alpha_0 + alpha[group]` where `alpha ~ normal(mu, sigma)`). This creates a non-identifiable sum. Either use a non-centered parameterization (`alpha_0 + sigma * z[group]`), or constrain group effects to sum-to-zero via `sum_to_zero_vector`.

## 7. Falsification Criteria

State what would **break** this model:
- **Targeted PPC:** Name one specific data feature the model *must* reproduce to be valid (e.g., "must capture the zero rate," "must reproduce lag-1 autocorrelation"). See `bayesian-model-diagnostics` for LOO-PIT shape-to-diagnosis mappings.
- **ELPD resolution:** How does this compare to the baseline? For i.i.d. data, see `bayesian-model-selection` for standard thresholds. For dependent data, specify the appropriate comparison method (rolling-origin, LFO-CV) as flagged in Section 2.
- **Parameter resolution:** Which parameter's credible interval answers the structural question?
