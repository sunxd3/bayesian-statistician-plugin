"""Shared utilities for Bayesian modeling with Stan."""

from .diagnostics import (
    ConvergenceResult,
    LOOResult,
    check_convergence,
    compute_loo,
    get_divergences,
)
from .io import load_posterior, read_json, save_results, to_arviz, write_json
from .paths import ensure_dir, project_root, resolve_path
from .stan import compile_model, fit_model, load_stan_data

__all__ = [
    "ConvergenceResult",
    "LOOResult",
    "check_convergence",
    "compile_model",
    "compute_loo",
    "ensure_dir",
    "fit_model",
    "get_divergences",
    "load_posterior",
    "load_stan_data",
    "project_root",
    "read_json",
    "resolve_path",
    "save_results",
    "to_arviz",
    "write_json",
]
