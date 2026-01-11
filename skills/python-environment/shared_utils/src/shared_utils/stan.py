"""Stan/CmdStanPy utilities."""

from __future__ import annotations

import json
from pathlib import Path

from cmdstanpy import CmdStanModel


def load_stan_data(data_path: Path | str) -> dict:
    """Load Stan data from JSON file."""
    with open(data_path) as f:
        return json.load(f)


def compile_model(stan_file: Path | str) -> CmdStanModel:
    """Compile a Stan model."""
    return CmdStanModel(stan_file=str(stan_file))


def fit_model(
    model: CmdStanModel,
    data: dict,
    *,
    chains: int = 4,
    warmup: int = 1000,
    sampling: int = 1000,
    adapt_delta: float = 0.9,
    output_dir: Path | str | None = None,
    show_progress: bool = True,
):
    """Fit a Stan model with sensible defaults.

    Returns the CmdStanMCMC fit object.
    """
    return model.sample(
        data=data,
        chains=chains,
        iter_warmup=warmup,
        iter_sampling=sampling,
        adapt_delta=adapt_delta,
        show_progress=show_progress,
        output_dir=str(output_dir) if output_dir else None,
        save_warmup=False,
    )
