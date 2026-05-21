---
name: statistical-diagnostics
description: Library of diagnostic tests for EDA and data quality assessment
---

# Statistical Diagnostics Reference

Use this skill when performing EDA to select appropriate diagnostic tests and interpret results. Each test exploits a specific mathematical property that should hold if assumptions are satisfied.

## Distribution Assessment

**Normality tests** (choose based on sample size):
- **Shapiro-Wilk**: Best for n < 50. W near 1.0 = normal. p < 0.05 rejects normality.
- **Jarque-Bera**: Best for n > 100. Tests skewness = 0 and kurtosis = 3.
- **Anderson-Darling**: Weights tails heavily. Use for risk/quality applications.
- **Practical rule**: If |skewness| < 2 and |kurtosis| < 7, normality is acceptable.

**QQ plot patterns**:
- Straight line → matches distribution
- Reverse S-shape → heavy tails
- S-shape → light tails
- Banana up → right skew
- Banana down → left skew

**Formal goodness-of-fit**:
- **Kolmogorov-Smirnov**: Max distance between empirical and theoretical CDF. Critical: 1.36/√n at α=0.05.
- **Anderson-Darling**: More sensitive than KS, especially in tails.

## Regression Diagnostics

**Heteroscedasticity** (non-constant variance):
- **Breusch-Pagan**: Regress squared residuals on X. LM = nR² ~ χ². p < 0.05 = heteroscedasticity.
- **White's test**: Adds X², X³, cross-products. Catches nonlinear variance patterns.
- **Goldfeld-Quandt**: Compare residual variances between low-X and high-X groups (F-test).

**Multicollinearity**:
- **VIF**: VIF = 1/(1-R²ⱼ). VIF > 5 investigate; VIF > 10 requires action.
- **Condition number**: √(λmax/λmin) > 30 = severe multicollinearity.

**Specification**:
- **Ramsey RESET**: Add ŷ², ŷ³ to model. Significant F-test = misspecification (but doesn't say which).

## Time Series Diagnostics

**Stationarity**:
- **ADF**: Tests for unit root. Critical value -2.86 at 5%. Fail to reject → difference the series.
- **KPSS**: Null is stationarity. Use with ADF:
  - ADF rejects + KPSS fails to reject → stationary
  - ADF fails + KPSS rejects → non-stationary, difference needed
  - Both reject → trend-stationary, detrend instead

**Autocorrelation**:
- **Durbin-Watson**: DW ≈ 2 = no autocorrelation. DW → 0 = positive; DW → 4 = negative.
- **Ljung-Box**: Tests multiple lags jointly. Q ~ χ²(h). For ARIMA residuals.

**ACF/PACF patterns**:
- Exponential ACF decay + PACF cutoff at p → AR(p)
- ACF cutoff at q + exponential PACF decay → MA(q)
- Both decay → ARMA(p,q)
- Slow ACF decay + PACF ≈ 1 at lag 1 → unit root

**ARCH effects** (volatility clustering):
- Regress ε̂² on lagged ε̂². T×R² ~ χ². Rejection → use GARCH.

## Count Data Diagnostics

**Overdispersion** (variance > mean):
- **Cameron-Trivedi**: Regress auxiliary variable on predictions. p < 0.05 = overdispersion.
- **Dispersion parameter**: φ = Pearson χ²/(n-p). φ > 2 = serious overdispersion.
- Fix: Use Negative Binomial or quasi-Poisson.

**Zero-inflation**: Observed zeros >> expected zeros from Poisson/NB → use ZIP or ZINB.

**Vuong test**: Compare non-nested count models. |V| > 1.96 = significant difference.

## Influence Diagnostics

- **Leverage (hᵢᵢ)**: Unusual X position. Flag: hᵢᵢ > 2(p+1)/n.
- **Cook's D**: Overall prediction change if deleted. Flag: D > 1 or D > 4/n.
- **DFBETAS**: Change in specific coefficient. Flag: |DFBETAS| > 2/√n.
- **Studentized residuals**: Y outliers. Flag: |t| > 3.
- **Mahalanobis distance**: Multivariate outlier. Compare to χ²(p, 0.999).

## Missing Data Diagnostics

**Mechanisms**:
- **MCAR**: Missingness random, unrelated to any variables.
- **MAR**: Missingness depends on observed variables (can handle with imputation).
- **MNAR**: Missingness depends on missing values (untestable, problematic).

**Little's MCAR test**: Compares means across missingness patterns. p < 0.05 rejects MCAR.

## Hierarchical Data

**ICC** = σ²between / (σ²between + σ²within). ICC > 0.05-0.10 → use multilevel models.

**Design effect** = 1 + (n̄ - 1) × ICC. Effective sample size = n/DEFF.

## Model Comparison

**AIC/BIC** (lower is better):
- ΔAIC 0-2: equivalent
- ΔAIC 4-7: considerably less support
- ΔAIC > 10: essentially no support

**Likelihood ratio test**: LRT = -2×(LL_reduced - LL_full) ~ χ²(df). Only for nested models.

## Key Thresholds Summary

| Test | Threshold | Interpretation |
|------|-----------|----------------|
| Shapiro-Wilk W | > 0.95 | Approximately normal |
| VIF | > 10 | Severe multicollinearity |
| Durbin-Watson | 1.5-2.5 | No serious autocorrelation |
| ADF critical | -2.86 | 5% significance |
| Cook's D | > 1 | High influence |
| ICC | > 0.05 | Use multilevel model |
| Dispersion φ | > 2 | Overdispersion |
