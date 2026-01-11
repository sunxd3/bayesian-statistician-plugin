"""I/O utilities for saving and loading results."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import arviz as az
import numpy as np
from cmdstanpy import CmdStanMCMC

from .paths import ensure_dir, resolve_path


def read_json(path: Path | str, *, base: Path | str | None = None) -> dict:
    """Read JSON from disk."""
    path = resolve_path(path, base=base)
    with open(path) as f:
        return json.load(f)


def write_json(
    path: Path | str,
    payload: Any,
    *,
    indent: int = 2,
    base: Path | str | None = None,
) -> None:
    """Write JSON to disk, creating parent directories if needed."""
    path = resolve_path(path, base=base)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=indent)


def _stan_var_names(fit: CmdStanMCMC) -> set[str]:
    """Get variable names from a CmdStanMCMC fit."""
    for attr in ("stan_vars_cols",):
        if hasattr(fit, attr):
            try:
                return set(getattr(fit, attr).keys())
            except Exception:
                continue
    metadata = getattr(fit, "metadata", None)
    if metadata is not None and hasattr(metadata, "stan_vars_cols"):
        try:
            return set(metadata.stan_vars_cols.keys())
        except Exception:
            pass
    return set()


def _coerce_payload(payload: Any) -> dict:
    """Convert payload to dict for JSON serialization."""
    if payload is None:
        return {}
    if is_dataclass(payload) and not isinstance(payload, type):
        return asdict(payload)
    if isinstance(payload, dict):
        return payload
    if hasattr(payload, "__dict__"):
        return {k: v for k, v in payload.__dict__.items() if not k.startswith("_")}
    return {"value": payload}


def _filter_present(names: Iterable[str], *, available: set[str]) -> list[str]:
    """Filter names to only those present in available set."""
    if not available:
        return list(names)
    return [name for name in names if name in available]


def to_arviz(
    fit: CmdStanMCMC,
    *,
    y_obs: np.ndarray | None = None,
    log_likelihood: str = "log_lik",
    posterior_predictive: list[str] | str | None = None,
    coords: dict | None = None,
    dims: dict | None = None,
) -> az.InferenceData:
    """Convert CmdStanPy fit to ArviZ InferenceData.

    Args:
        fit: CmdStanMCMC fit object
        y_obs: Observed y values (for observed_data group)
        log_likelihood: Name of log_lik variable in Stan model
        posterior_predictive: Names of posterior predictive variables
        coords: Coordinate labels
        dims: Dimension names for variables

    Returns:
        ArviZ InferenceData object
    """
    observed_data = {"y": y_obs} if y_obs is not None else None
    available = _stan_var_names(fit)

    if posterior_predictive is None:
        posterior_predictive = (
            ["y_rep"] if ("y_rep" in available or not available) else None
        )
    elif isinstance(posterior_predictive, str):
        posterior_predictive = [posterior_predictive]

    if posterior_predictive:
        posterior_predictive = _filter_present(
            posterior_predictive, available=available
        )
        if not posterior_predictive:
            posterior_predictive = None

    log_likelihood_name = (
        log_likelihood
        if log_likelihood and (log_likelihood in available or not available)
        else None
    )

    return az.from_cmdstanpy(
        fit,
        log_likelihood=log_likelihood_name,
        posterior_predictive=posterior_predictive,
        observed_data=observed_data,
        coords=coords,
        dims=dims,
    )


def save_results(
    idata: az.InferenceData,
    output_dir: Path | str,
    *,
    convergence: Any | None = None,
    loo: Any | None = None,
) -> None:
    """Save InferenceData and diagnostic results.

    Args:
        idata: ArviZ InferenceData
        output_dir: Directory to save results
        convergence: Convergence diagnostics (dict or dataclass)
        loo: LOO-CV results (dict or dataclass)
    """
    output_dir = ensure_dir(output_dir)

    # Save InferenceData
    idata.to_netcdf(str(output_dir / "posterior.nc"))

    # Save convergence results
    if convergence:
        write_json(output_dir / "convergence.json", _coerce_payload(convergence))

    # Save LOO results
    if loo:
        write_json(output_dir / "loo.json", _coerce_payload(loo))


def load_posterior(
    output_dir: Path | str,
    *,
    base: Path | str | None = None,
) -> az.InferenceData:
    """Load InferenceData from output directory."""
    output_dir = resolve_path(output_dir, base=base)
    return az.from_netcdf(output_dir / "posterior.nc")
