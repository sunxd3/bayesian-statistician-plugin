"""MCMC diagnostics utilities."""

from __future__ import annotations

from dataclasses import dataclass

import arviz as az
import numpy as np


@dataclass
class ConvergenceResult:
    """Convergence diagnostic results."""

    max_rhat: float
    min_ess_bulk: float
    min_ess_tail: float
    n_divergent: int
    converged: bool
    rhat_threshold: float = 1.01
    ess_bulk_threshold: float = 400
    ess_tail_threshold: float = 400
    max_divergences: int = 0

    def __str__(self) -> str:
        status = "PASSED" if self.converged else "FAILED"
        return (
            f"Convergence: {status}\n"
            f"  Max R-hat: {self.max_rhat:.4f} (target < {self.rhat_threshold:.2f})\n"
            f"  Min ESS bulk: {self.min_ess_bulk:.0f} (target > {self.ess_bulk_threshold:.0f})\n"
            f"  Min ESS tail: {self.min_ess_tail:.0f} (target > {self.ess_tail_threshold:.0f})\n"
            f"  Divergences: {self.n_divergent} (target <= {self.max_divergences})"
        )


def get_divergences(idata: az.InferenceData) -> int:
    """Get number of divergent transitions from InferenceData."""
    if "sample_stats" not in idata.groups():
        return 0
    sample_stats = getattr(idata, "sample_stats")
    return int(sample_stats["diverging"].sum())


def check_convergence(
    idata: az.InferenceData,
    var_names: list[str] | None = None,
    *,
    rhat_threshold: float = 1.01,
    ess_bulk_threshold: float = 400,
    ess_tail_threshold: float = 400,
    max_divergences: int = 0,
) -> ConvergenceResult:
    """Check MCMC convergence using ArviZ.

    Args:
        idata: ArviZ InferenceData object
        var_names: Variables to check (None = all)
        rhat_threshold: Maximum acceptable R-hat
        ess_bulk_threshold: Minimum acceptable ESS bulk
        ess_tail_threshold: Minimum acceptable ESS tail
        max_divergences: Maximum acceptable divergent transitions

    Returns:
        ConvergenceResult with diagnostics
    """
    summary = az.summary(idata, var_names=var_names)

    max_rhat = float(summary["r_hat"].max())
    min_ess_bulk = float(summary["ess_bulk"].min())
    min_ess_tail = float(summary["ess_tail"].min())
    n_divergent = get_divergences(idata)

    converged = (
        max_rhat < rhat_threshold
        and min_ess_bulk > ess_bulk_threshold
        and min_ess_tail > ess_tail_threshold
        and n_divergent <= max_divergences
    )

    return ConvergenceResult(
        max_rhat=max_rhat,
        min_ess_bulk=min_ess_bulk,
        min_ess_tail=min_ess_tail,
        n_divergent=n_divergent,
        converged=converged,
        rhat_threshold=rhat_threshold,
        ess_bulk_threshold=ess_bulk_threshold,
        ess_tail_threshold=ess_tail_threshold,
        max_divergences=max_divergences,
    )


@dataclass
class LOOResult:
    """LOO-CV results."""

    elpd_loo: float
    se: float
    p_loo: float
    k_good: int
    k_ok: int
    k_bad: int
    k_very_bad: int

    def __str__(self) -> str:
        total = self.k_good + self.k_ok + self.k_bad + self.k_very_bad
        return (
            f"LOO-CV Results:\n"
            f"  ELPD: {self.elpd_loo:.1f} +/- {self.se:.1f}\n"
            f"  p_loo: {self.p_loo:.1f}\n"
            f"  Pareto k: {self.k_good} good, {self.k_ok} ok, "
            f"{self.k_bad} bad, {self.k_very_bad} very bad "
            f"(n={total})"
        )


def compute_loo(idata: az.InferenceData) -> LOOResult:
    """Compute LOO-CV with Pareto k diagnostics.

    Args:
        idata: ArviZ InferenceData with log_likelihood group

    Returns:
        LOOResult with ELPD and Pareto k breakdown
    """
    loo = az.loo(idata, pointwise=True)
    pareto_k = loo.pareto_k.values

    return LOOResult(
        elpd_loo=float(loo.elpd_loo),
        se=float(loo.se),
        p_loo=float(loo.p_loo),
        k_good=int(np.sum(pareto_k < 0.5)),
        k_ok=int(np.sum((pareto_k >= 0.5) & (pareto_k < 0.7))),
        k_bad=int(np.sum((pareto_k >= 0.7) & (pareto_k < 1.0))),
        k_very_bad=int(np.sum(pareto_k >= 1.0)),
    )
