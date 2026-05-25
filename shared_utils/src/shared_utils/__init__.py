"""Shared utilities for Bayesian modeling with Stan."""

from .diagnostics import (
    ConvergenceResult,
    LOOResult,
    check_convergence,
    compute_loo,
    get_divergences,
)
from .fit_pipeline import (
    FitResult,
    cleanup_csv_files,
    fit_and_summarize,
)
from .io import (
    NumpyEncoder,
    to_arviz_prior,
    write_json,
)
from .paths import ensure_dir, project_root, resolve_path
from .stan import compile_model, fit_model

__all__ = [
    "ConvergenceResult",
    "FitResult",
    "LOOResult",
    "NumpyEncoder",
    "check_convergence",
    "cleanup_csv_files",
    "compile_model",
    "compute_loo",
    "ensure_dir",
    "fit_and_summarize",
    "fit_model",
    "get_divergences",
    "project_root",
    "resolve_path",
    "to_arviz_prior",
    "write_json",
]
