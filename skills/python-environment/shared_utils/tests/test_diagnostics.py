from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import shared_utils.diagnostics as diagnostics


@dataclass
class DummySummary:
    data: dict[str, np.ndarray]

    def __getitem__(self, key: str) -> np.ndarray:
        return self.data[key]


class DummySampleStats:
    def __init__(self, diverging: np.ndarray) -> None:
        self._diverging = diverging

    def __getitem__(self, key: str) -> np.ndarray:
        if key != "diverging":
            raise KeyError(key)
        return self._diverging


class DummyInferenceData:
    def __init__(self, diverging: np.ndarray | None = None) -> None:
        self.sample_stats = (
            DummySampleStats(diverging) if diverging is not None else None
        )

    def groups(self) -> list[str]:
        return ["sample_stats"] if self.sample_stats is not None else []


def test_get_divergences() -> None:
    idata = DummyInferenceData(diverging=np.array([0, 1, 0, 1], dtype=int))

    assert diagnostics.get_divergences(idata) == 2


def test_check_convergence(monkeypatch) -> None:
    summary = DummySummary(
        {
            "r_hat": np.array([1.0, 1.02]),
            "ess_bulk": np.array([500.0, 450.0]),
            "ess_tail": np.array([480.0, 460.0]),
        }
    )
    monkeypatch.setattr(diagnostics.az, "summary", lambda *a, **k: summary)

    idata = DummyInferenceData(diverging=np.array([0, 0, 1], dtype=int))

    result = diagnostics.check_convergence(
        idata,
        rhat_threshold=1.03,
        ess_bulk_threshold=400,
        ess_tail_threshold=400,
        max_divergences=1,
    )

    assert result.converged is True
    assert result.max_rhat == 1.02
    assert result.min_ess_bulk == 450.0
    assert result.min_ess_tail == 460.0
    assert result.n_divergent == 1


def test_compute_loo(monkeypatch) -> None:
    class DummyLoo:
        elpd_loo = 12.5
        se = 1.1
        p_loo = 3.2
        pareto_k = type("K", (), {"values": np.array([0.4, 0.6, 0.8, 1.2])})()

    monkeypatch.setattr(diagnostics.az, "loo", lambda *a, **k: DummyLoo())

    result = diagnostics.compute_loo(DummyInferenceData())

    assert result.elpd_loo == 12.5
    assert result.se == 1.1
    assert result.p_loo == 3.2
    assert (result.k_good, result.k_ok, result.k_bad, result.k_very_bad) == (1, 1, 1, 1)
