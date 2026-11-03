"""build.stale.* directories are excluded from backups: the pattern is in the packaged excludes file,
and rsync honors it against a real tree."""

import os
import shutil
import subprocess

import pytest

from backuptools import lib

PATTERN = "build.stale.*/"


@pytest.mark.unit
def test_packaged_excludes_file_lists_build_stale():
    with open(lib.DEFAULT_EXCLUDES, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip()]
    assert PATTERN in lines


@pytest.mark.unit
@pytest.mark.skipif(shutil.which("rsync") is None, reason="rsync not installed")
def test_rsync_skips_build_stale_directories(tmp_path):
    src = tmp_path / "src"
    (src / "build.stale.123" / "lib").mkdir(parents=True)
    (src / "build.stale.123" / "lib" / "a.py").write_text("x")
    (src / "keep" / "lib").mkdir(parents=True)
    (src / "keep" / "lib" / "b.py").write_text("y")
    dst = tmp_path / "dst"
    out = subprocess.run(
        ["rsync", "--recursive", f"--exclude-from={lib.DEFAULT_EXCLUDES}", f"{src}/", f"{dst}/"],
        capture_output=True, text=True, check=True,
    )
    assert os.path.exists(dst / "keep" / "lib" / "b.py")
    assert not os.path.exists(dst / "build.stale.123")
