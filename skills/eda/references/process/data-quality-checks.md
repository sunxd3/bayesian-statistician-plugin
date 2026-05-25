# Data Quality Checks

Always complete these checks regardless of focus area:

- **Missingness**: per-column and per-row rates, flag columns >30% missing
- **Missingness mechanism**: does missingness correlate with other variables, time, or groups? If so, report top predictors
- **Duplicates**: row-level and per-identifier
- **Invalid values**: constant columns, impossible ranges, sentinel values ("NA", "?", "-999")
- **Type issues**: numerics stored as strings, mixed-type columns
