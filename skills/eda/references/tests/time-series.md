# Time Series Diagnostics

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
