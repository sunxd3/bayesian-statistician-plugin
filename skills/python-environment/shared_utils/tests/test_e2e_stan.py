from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import cmdstanpy

import shared_utils as su


def _require_cmdstan() -> None:
    try:
        path = cmdstanpy.cmdstan_path()
    except Exception as exc:  # pragma: no cover - skip when CmdStan missing
        pytest.skip(f"CmdStan not available: {exc}")
    if not Path(path).exists():
        pytest.skip("CmdStan path does not exist")


def _stan_cache_dir() -> Path:
    cache_dir = Path(__file__).resolve().parents[1] / ".cmdstan_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def test_e2e_stan_workflow(tmp_path: Path) -> None:
    _require_cmdstan()

    stan_code = """
    data {
      int<lower=1> N;
      vector[N] y;
    }
    parameters {
      real mu;
      real<lower=0> sigma;
    }
    model {
      y ~ normal(mu, sigma);
    }
    generated quantities {
      vector[N] y_rep;
      vector[N] log_lik;
      for (n in 1:N) {
        y_rep[n] = normal_rng(mu, sigma);
        log_lik[n] = normal_lpdf(y[n] | mu, sigma);
      }
    }
    """

    cache_dir = _stan_cache_dir()
    stan_file = cache_dir / "model.stan"
    if not stan_file.exists() or stan_file.read_text() != stan_code:
        stan_file.write_text(stan_code)
    data = {"N": 6, "y": [1.0, 0.8, 1.2, 1.1, 0.9, 1.3]}
    data_path = tmp_path / "data.json"
    data_path.write_text(json.dumps(data))

    model = su.compile_model(stan_file)
    fit = su.fit_model(
        model,
        su.load_stan_data(data_path),
        chains=2,
        warmup=50,
        sampling=50,
        adapt_delta=0.8,
        show_progress=False,
        output_dir=tmp_path,
    )

    idata = su.to_arviz(
        fit,
        y_obs=np.array(data["y"], dtype=float),
        log_likelihood="log_lik",
        posterior_predictive=["y_rep"],
    )

    convergence = su.check_convergence(
        idata,
        rhat_threshold=1.5,
        ess_bulk_threshold=10,
        ess_tail_threshold=10,
        max_divergences=10,
    )
    loo = su.compute_loo(idata)

    output_dir = tmp_path / "results"
    su.save_results(idata, output_dir, convergence=convergence, loo=loo)
    loaded = su.load_posterior(output_dir)

    assert "posterior" in loaded.groups()
    assert np.isfinite(convergence.min_ess_bulk)
    assert loo.k_good + loo.k_ok + loo.k_bad + loo.k_very_bad == data["N"]
