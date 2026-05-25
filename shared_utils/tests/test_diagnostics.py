"""Tests for shared_utils.diagnostics module (uses real InferenceData, not mocks)."""

from __future__ import annotations

import arviz as az
import numpy as np

from shared_utils.diagnostics import (
    ConvergenceResult,
    LOOResult,
    check_convergence,
    compute_loo,
    get_divergences,
)


class TestGetDivergences:
    """Tests for get_divergences()."""

    def test_counts_correctly_no_divergences(self, eight_schools_posterior_idata):
        """get_divergences() returns 0 for well-behaved idata."""
        n = get_divergences(eight_schools_posterior_idata)
        assert n == 0

    def test_counts_correctly_with_divergences(self, divergent_idata):
        """get_divergences() counts divergences correctly."""
        n = get_divergences(divergent_idata)
        assert n == 60  # 15 per chain * 4 chains

    def test_no_sample_stats(self):
        """get_divergences() returns 0 if no sample_stats group."""
        idata = az.from_dict(posterior={"x": np.random.randn(4, 100)})
        assert get_divergences(idata) == 0


class TestCheckConvergence:
    """Tests for check_convergence()."""

    def test_converged_true_for_well_behaved(self, eight_schools_posterior_idata):
        """check_convergence() returns converged=True for well-behaved idata."""
        result = check_convergence(eight_schools_posterior_idata)
        assert isinstance(result, ConvergenceResult)
        assert result.converged is True
        assert result.n_divergent == 0
        assert result.max_rhat < 1.01

    def test_converged_false_for_high_rhat(self, divergent_idata):
        """check_convergence() returns converged=False when r_hat > threshold."""
        result = check_convergence(divergent_idata)
        assert result.converged is False
        # Should fail on at least one of: rhat, divergences
        assert result.max_rhat > 1.01 or result.n_divergent > 0

    def test_detects_divergences(self, divergent_idata):
        """check_convergence() detects divergences."""
        result = check_convergence(divergent_idata)
        assert result.n_divergent > 0
        assert result.n_divergent == 60

    def test_respects_custom_thresholds(self, eight_schools_posterior_idata):
        """check_convergence() respects custom thresholds."""
        # Use extremely tight thresholds to force failure
        result = check_convergence(
            eight_schools_posterior_idata,
            rhat_threshold=0.99,  # impossibly tight
            ess_bulk_threshold=1_000_000,  # impossibly high
            ess_tail_threshold=1_000_000,
        )
        assert result.converged is False
        assert result.rhat_threshold == 0.99
        assert result.ess_bulk_threshold == 1_000_000

    def test_str_representation(self, eight_schools_posterior_idata):
        """ConvergenceResult.__str__() produces readable output."""
        result = check_convergence(eight_schools_posterior_idata)
        s = str(result)
        assert "PASSED" in s or "FAILED" in s
        assert "R-hat" in s
        assert "ESS bulk" in s


class TestComputeLoo:
    """Tests for compute_loo()."""

    def test_returns_correct_structure(self, eight_schools_posterior_idata):
        """compute_loo() returns correct LOOResult structure."""
        result = compute_loo(eight_schools_posterior_idata)
        assert isinstance(result, LOOResult)
        assert isinstance(result.elpd_loo, float)
        assert isinstance(result.se, float)
        assert isinstance(result.p_loo, float)
        assert isinstance(result.k_good, int)
        assert isinstance(result.k_ok, int)
        assert isinstance(result.k_bad, int)
        assert isinstance(result.k_very_bad, int)

    def test_pareto_k_breakdown_sums(self, eight_schools_posterior_idata):
        """compute_loo() pareto_k breakdown sums to number of observations."""
        result = compute_loo(eight_schools_posterior_idata)
        total = result.k_good + result.k_ok + result.k_bad + result.k_very_bad
        assert total == 8  # 8 schools

    def test_elpd_is_negative(self, eight_schools_posterior_idata):
        """compute_loo() elpd_loo should be negative for realistic data."""
        result = compute_loo(eight_schools_posterior_idata)
        assert result.elpd_loo < 0

    def test_str_representation(self, eight_schools_posterior_idata):
        """LOOResult.__str__() produces readable output."""
        result = compute_loo(eight_schools_posterior_idata)
        s = str(result)
        assert "ELPD" in s
        assert "Pareto k" in s
