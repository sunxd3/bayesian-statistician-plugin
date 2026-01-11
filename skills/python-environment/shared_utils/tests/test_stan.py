from __future__ import annotations

import json
from pathlib import Path

import shared_utils.stan as stan


def test_load_stan_data(tmp_path: Path) -> None:
    data = {"n": 3, "y": [1, 2, 3]}
    path = tmp_path / "data.json"
    path.write_text(json.dumps(data))

    loaded = stan.load_stan_data(path)

    assert loaded == data


def test_compile_model(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    class DummyModel:
        def __init__(self, stan_file: str) -> None:
            captured["stan_file"] = stan_file

    monkeypatch.setattr(stan, "CmdStanModel", DummyModel)
    stan_file = tmp_path / "model.stan"
    stan_file.write_text("// model")

    model = stan.compile_model(stan_file)

    assert isinstance(model, DummyModel)
    assert captured["stan_file"] == str(stan_file)


def test_fit_model(monkeypatch) -> None:
    class DummyModel:
        def __init__(self) -> None:
            self.calls: list[dict[str, object]] = []

        def sample(self, **kwargs):
            self.calls.append(kwargs)
            return "fit"

    model = DummyModel()

    fit = stan.fit_model(
        model,
        data={"x": [1, 2]},
        chains=2,
        warmup=10,
        sampling=20,
        adapt_delta=0.95,
        output_dir="out",
        show_progress=False,
    )

    assert fit == "fit"
    assert model.calls
    call = model.calls[-1]
    assert call["iter_warmup"] == 10
    assert call["iter_sampling"] == 20
    assert call["chains"] == 2
    assert call["adapt_delta"] == 0.95
    assert call["output_dir"] == "out"
    assert call["show_progress"] is False
