"""Project path helpers."""

from __future__ import annotations

import os
from pathlib import Path

_PROJECT_ROOT: Path | None = None


def project_root(env_var: str = "PROJECT_ROOT") -> Path:
    """Return the project root (directory containing pyproject.toml).

    Searches upward from the caller's location, or uses the environment
    variable specified by `env_var` if set.
    """
    global _PROJECT_ROOT
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT

    env_root = os.getenv(env_var)
    if env_root:
        _PROJECT_ROOT = Path(env_root).expanduser().resolve()
        return _PROJECT_ROOT

    here = Path.cwd().resolve()
    for parent in [here, *here.parents]:
        if (parent / "pyproject.toml").exists():
            _PROJECT_ROOT = parent
            return _PROJECT_ROOT

    _PROJECT_ROOT = here
    return _PROJECT_ROOT


def resolve_path(path: Path | str, *, base: Path | str | None = None) -> Path:
    """Resolve a path relative to base (defaults to project root)."""
    path = Path(path).expanduser()
    if path.is_absolute():
        return path
    base_dir = Path(base).expanduser() if base is not None else project_root()
    return (base_dir / path).resolve()


def ensure_dir(path: Path | str, *, base: Path | str | None = None) -> Path:
    """Create a directory and return it."""
    path = resolve_path(path, base=base)
    path.mkdir(parents=True, exist_ok=True)
    return path
