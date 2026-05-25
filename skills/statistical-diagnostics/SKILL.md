---
name: statistical-diagnostics
description: Library of diagnostic tests for EDA and data quality assessment. Each test exploits a specific mathematical property that should hold if assumptions are satisfied.
user-invocable: false
---

# Statistical Diagnostics

Use during EDA to select and interpret diagnostic tests. Load only the references relevant to your data shape — most datasets need two or three of these:

- `references/distribution.md` — normality tests (Shapiro-Wilk, Jarque-Bera, Anderson-Darling), QQ-plot patterns, formal goodness-of-fit (KS, AD). Use for any continuous outcome.
- `references/regression.md` — heteroscedasticity (Breusch-Pagan, White, Goldfeld-Quandt), multicollinearity (VIF, condition number), specification (Ramsey RESET), and influence diagnostics (leverage, Cook's D, DFBETAS, Studentized residuals, Mahalanobis).
- `references/time-series.md` — stationarity (ADF, KPSS), autocorrelation (Durbin-Watson, Ljung-Box), ACF/PACF patterns, ARCH effects.
- `references/count.md` — overdispersion (Cameron-Trivedi, dispersion parameter), zero-inflation, Vuong test for non-nested models.
- `references/missing-and-hierarchical.md` — MCAR/MAR/MNAR mechanisms, Little's test, ICC, design effect.
- `references/model-comparison.md` — AIC/BIC, likelihood ratio test.

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
