from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import arviz as az

from shared_utils.io import (
    _coerce_payload,
    _filter_present,
    _stan_var_names,
    read_json,
    to_arviz,
    write_json,
)


@dataclass
class Payload:
    name: str
    value: int


class ObjWithAttrs:
    def __init__(self) -> None:
        self.visible = 1
        self._hidden = 2


def test_coerce_payload_dataclass() -> None:
    payload = Payload(name="alpha", value=3)

    coerced = _coerce_payload(payload)

    assert coerced == {"name": "alpha", "value": 3}


def test_coerce_payload_object_filters_private() -> None:
    payload = ObjWithAttrs()

    coerced = _coerce_payload(payload)

    assert coerced == {"visible": 1}


def test_filter_present() -> None:
    names = ["a", "b", "c"]
    available = {"b", "d"}

    filtered = _filter_present(names, available=available)

    assert filtered == ["b"]


def test_read_write_json(tmp_path: Path) -> None:
    payload = {"a": 1, "b": [1, 2, 3]}
    path = tmp_path / "out" / "data.json"

    write_json(path, payload, indent=2)
    loaded = read_json(path)

    assert loaded == payload

    raw = json.loads(path.read_text())
    assert raw == payload


class FitWithVars:
    def __init__(self, keys: list[str]) -> None:
        self.stan_vars_cols = {key: None for key in keys}


class FitWithMetadata:
    def __init__(self, keys: list[str]) -> None:
        class Metadata:
            def __init__(self, keys: list[str]) -> None:
                self.stan_vars_cols = {key: None for key in keys}

        self.metadata = Metadata(keys)


def test_stan_var_names_primary() -> None:
    fit = FitWithVars(["alpha", "beta"])

    names = _stan_var_names(fit)

    assert names == {"alpha", "beta"}


def test_stan_var_names_metadata_fallback() -> None:
    fit = FitWithMetadata(["theta"])

    names = _stan_var_names(fit)

    assert names == {"theta"}


def test_to_arviz_uses_defaults(monkeypatch) -> None:
    fit = FitWithVars(["log_lik", "y_rep"])
    called: dict[str, object] = {}

    def fake_from_cmdstanpy(*args, **kwargs):
        called["args"] = args
        called["kwargs"] = kwargs
        return az.InferenceData()

    monkeypatch.setattr(az, "from_cmdstanpy", fake_from_cmdstanpy)

    idata = to_arviz(fit, y_obs=None)

    assert isinstance(idata, az.InferenceData)
    assert called["args"][0] is fit
    assert called["kwargs"]["log_likelihood"] == "log_lik"
    assert called["kwargs"]["posterior_predictive"] == ["y_rep"]
    assert called["kwargs"]["observed_data"] is None


def test_to_arviz_filters_missing(monkeypatch) -> None:
    fit = FitWithVars(["log_lik"])
    called: dict[str, object] = {}

    def fake_from_cmdstanpy(*args, **kwargs):
        called["kwargs"] = kwargs
        return az.InferenceData()

    monkeypatch.setattr(az, "from_cmdstanpy", fake_from_cmdstanpy)

    to_arviz(
        fit,
        posterior_predictive=["y_rep"],
        log_likelihood="missing",
        y_obs=None,
    )

    assert called["kwargs"]["posterior_predictive"] is None
    assert called["kwargs"]["log_likelihood"] is None
