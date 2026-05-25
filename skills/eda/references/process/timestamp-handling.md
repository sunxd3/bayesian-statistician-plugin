# Timestamp and Time-Series Profiling

When timestamps are present:

- Preserve the raw timestamp column; create a separate parsed column
- Report parse success rate and any timezone assumptions (do not silently convert)
- Infer frequency from mode of time deltas; state evidence
- Check for gaps: expected vs actual timestamps, longest gap spans
- For panel data, report per-entity coverage

For statistical tests on the resulting time series (ADF, KPSS, Durbin-Watson, Ljung-Box, ACF/PACF, ARCH), see `references/tests/time-series.md`.
