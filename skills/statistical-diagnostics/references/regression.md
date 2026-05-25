# Regression Diagnostics

**Heteroscedasticity** (non-constant variance):
- **Breusch-Pagan**: Regress squared residuals on X. LM = nR² ~ χ². p < 0.05 = heteroscedasticity.
- **White's test**: Adds X², X³, cross-products. Catches nonlinear variance patterns.
- **Goldfeld-Quandt**: Compare residual variances between low-X and high-X groups (F-test).

**Multicollinearity**:
- **VIF**: VIF = 1/(1-R²ⱼ). VIF > 5 investigate; VIF > 10 requires action.
- **Condition number**: √(λmax/λmin) > 30 = severe multicollinearity.

**Specification**:
- **Ramsey RESET**: Add ŷ², ŷ³ to model. Significant F-test = misspecification (but doesn't say which).

## Influence Diagnostics

- **Leverage (hᵢᵢ)**: Unusual X position. Flag: hᵢᵢ > 2(p+1)/n.
- **Cook's D**: Overall prediction change if deleted. Flag: D > 1 or D > 4/n.
- **DFBETAS**: Change in specific coefficient. Flag: |DFBETAS| > 2/√n.
- **Studentized residuals**: Y outliers. Flag: |t| > 3.
- **Mahalanobis distance**: Multivariate outlier. Compare to χ²(p, 0.999).
