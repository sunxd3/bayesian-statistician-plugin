# Standardization

Apply these transformations to produce the canonical cleaned dataset (`data.cleaned.parquet`) that downstream agents can trust. Standardization is mechanical cleanup driven by the semantic audit; it does not reinterpret what columns mean.

## Column names

- Convert to `snake_case` (lowercase, underscores for spaces/punctuation).
- Strip leading/trailing whitespace.
- Replace non-alphanumeric characters with `_`.
- Disambiguate duplicates with a numeric suffix (`col`, `col_2`, ...).

## Missing values

- Convert sentinel strings to NaN: `"NA"`, `"N/A"`, `"NULL"`, `"null"`, `""`, `"?"`, `"-"`, `"-999"`, `-999`.
- Domain-specific sentinels (e.g., `99` in survey data) require evidence from a data dictionary or distribution shape; flag and convert with justification.

## Types

- Parse timestamp strings to datetime; preserve timezone if present, do not silently convert.
- Coerce numerics stored as strings (`"1,234"` → `1234`, `"3.14"` → `3.14`).
- Booleans: harmonize `"yes"/"no"`, `"true"/"false"`, `0/1` to bool.
- Store small-cardinality categorical columns as `category` dtype.

## Categorical encoding

- Trim whitespace.
- Normalize case only when purely cosmetic (e.g., `"Yes"` vs `"yes"`); preserve semantically meaningful case.
- Merge synonyms only with evidence (`"M"` vs `"Male"` → flag, propose, justify).
- Do not impose ordinal order without evidence from a data dictionary or domain knowledge.

## What NOT to standardize here

- **Scaling / centering / log transforms** — belong in modeling (prior setting).
- **Imputation** — leave NaNs for the modeling phase to handle explicitly.
- **Outlier removal** — flag, do not drop.
- **Feature engineering** — derived columns belong in modeling.

## Output

Emit `data.cleaned.parquet` (Parquet preserves dtypes). Document the final schema (column names + dtypes) in the Data Semantics Audit section of `eda_report.md` so downstream agents can rely on it.
