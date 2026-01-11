from __future__ import annotations

import os
from pathlib import Path

import shared_utils.paths as paths
from shared_utils.paths import ensure_dir, project_root, resolve_path


def test_project_root_env_var(tmp_path: Path, monkeypatch) -> None:
    custom_root = tmp_path / "custom_root"
    custom_root.mkdir()
    monkeypatch.setenv("PROJECT_ROOT", str(custom_root))
    paths._PROJECT_ROOT = None

    root = project_root()

    assert root == custom_root.resolve()


def test_project_root_searches_upward(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    nested = root / "a" / "b"
    nested.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname='x'\n")
    monkeypatch.delenv("PROJECT_ROOT", raising=False)
    paths._PROJECT_ROOT = None

    monkeypatch.chdir(nested)
    detected = project_root()

    assert detected == root.resolve()


def test_resolve_path_relative(tmp_path: Path) -> None:
    base = tmp_path / "base"
    base.mkdir()

    resolved = resolve_path("data/file.json", base=base)

    assert resolved == (base / "data" / "file.json").resolve()


def test_resolve_path_absolute(tmp_path: Path) -> None:
    absolute = tmp_path / "abs.txt"

    resolved = resolve_path(absolute)

    assert resolved == absolute


def test_ensure_dir_creates(tmp_path: Path) -> None:
    target = tmp_path / "a" / "b"

    ensured = ensure_dir(target)

    assert ensured == target.resolve()
    assert ensured.exists()
    assert ensured.is_dir()
