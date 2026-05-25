# Distribution Assessment

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
