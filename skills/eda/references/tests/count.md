# Count Data Diagnostics

**Overdispersion** (variance > mean):
- **Cameron-Trivedi**: Regress auxiliary variable on predictions. p < 0.05 = overdispersion.
- **Dispersion parameter**: φ = Pearson χ²/(n-p). φ > 2 = serious overdispersion.
- Fix: Use Negative Binomial or quasi-Poisson.

**Zero-inflation**: Observed zeros >> expected zeros from Poisson/NB → use ZIP or ZINB.

**Vuong test**: Compare non-nested count models. |V| > 1.96 = significant difference.
