"""Tests for shared_utils.paths module."""

from __future__ import annotations

from pathlib import Path

from shared_utils.paths import ensure_dir, resolve_path


class TestEnsureDir:
    """Tests for ensure_dir()."""

    def test_creates_nested_directories(self, tmp_path: Path):
        target = tmp_path / "a" / "b" / "c"
        assert not target.exists()

        result = ensure_dir(target)
        assert target.exists()
        assert target.is_dir()
        assert result == target

    def test_idempotent(self, tmp_path: Path):
        target = tmp_path / "already_exists"
        target.mkdir()

        result = ensure_dir(target)
        assert result == target

    def test_with_string_path(self, tmp_path: Path):
        target = str(tmp_path / "str_dir")
        result = ensure_dir(target)
        assert Path(target).exists()
        assert isinstance(result, Path)


class TestResolvePath:
    """Tests for resolve_path()."""

    def test_absolute_path_unchanged(self):
        p = resolve_path("/absolute/path")
        assert p == Path("/absolute/path")

    def test_relative_path_with_base(self, tmp_path: Path):
        p = resolve_path("subdir/file.txt", base=tmp_path)
        assert p == (tmp_path / "subdir" / "file.txt").resolve()

    def test_tilde_expansion(self):
        p = resolve_path("~/test.txt")
        assert "~" not in str(p)

    def test_relative_without_base_uses_project_root(self):
        """resolve_path() with no base uses project_root()."""
        p = resolve_path("some/file.txt")
        # Should be resolved (absolute)
        assert p.is_absolute()
