# Missing Data and Hierarchical Structure

## Missing Data Diagnostics

**Mechanisms**:
- **MCAR**: Missingness random, unrelated to any variables.
- **MAR**: Missingness depends on observed variables (can handle with imputation).
- **MNAR**: Missingness depends on missing values (untestable, problematic).

**Little's MCAR test**: Compares means across missingness patterns. p < 0.05 rejects MCAR.

## Hierarchical Data

**ICC** = σ²between / (σ²between + σ²within). ICC > 0.05-0.10 → use multilevel models.

**Design effect** = 1 + (n̄ - 1) × ICC. Effective sample size = n/DEFF.
