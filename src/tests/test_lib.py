import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backuptools import lib


pytestmark = pytest.mark.unit


class TestConstants:
    def test_packagename(self):
        assert lib.PACKAGENAME == "backuptools"

    def test_default_staging(self):
        assert lib.DEFAULT_STAGING == "/srv/backups/"

    def test_default_backupdevice(self):
        assert lib.DEFAULT_BACKUPDEVICE == "/run/media/jam/BEA6-BBCE/"

    def test_source_base(self):
        assert lib.SOURCE_BASE == "/home/opencode/data/work"

    def test_default_excludes(self):
        assert "rsync-excludes.txt" in lib.DEFAULT_EXCLUDES
        assert os.path.isabs(lib.DEFAULT_EXCLUDES)


class TestBuildargs:
    def test_returns_argumentparser(self):
        parser = lib.buildargs()
        assert parser is not None

    def test_has_debug_flag(self):
        parser = lib.buildargs()
        args = parser.parse_args(["--debug", "project1"])
        assert args.debug is True

    def test_has_projects_positional(self):
        parser = lib.buildargs()
        args = parser.parse_args(["project1", "project2"])
        assert args.projects == ["project1", "project2"]

    def test_has_staging_option(self):
        parser = lib.buildargs()
        args = parser.parse_args(["--staging", "/custom/staging", "project1"])
        assert args.staging == "/custom/staging"

    def test_default_staging(self):
        parser = lib.buildargs()
        args = parser.parse_args(["project1"])
        assert args.staging == "/srv/backups/"

    def test_has_backupdevice_option(self):
        parser = lib.buildargs()
        args = parser.parse_args(["--backupdevice", "/custom/device", "project1"])
        assert args.backupdevice == "/custom/device"

    def test_has_excludes_option(self):
        parser = lib.buildargs()
        args = parser.parse_args(["--excludes", "/custom/excludes.txt", "project1"])
        assert args.excludes == "/custom/excludes.txt"

    def test_has_dry_run_flag(self):
        parser = lib.buildargs()
        args = parser.parse_args(["--dry-run", "project1"])
        assert args.dry_run is True

    def test_has_verbose_flag(self):
        parser = lib.buildargs()
        args = parser.parse_args(["--verbose", "project1"])
        assert args.verbose is True

    def test_verbose_default_true(self):
        parser = lib.buildargs()
        args = parser.parse_args(["project1"])
        assert args.verbose is True

    def test_has_no_mount_check_flag(self):
        parser = lib.buildargs()
        args = parser.parse_args(["--no-mount-check", "project1"])
        assert args.no_mount_check is True

    def test_has_stage_only_flag(self):
        parser = lib.buildargs()
        args = parser.parse_args(["--stage-only", "project1"])
        assert args.stage_only is True

    def test_has_thumb_only_flag(self):
        parser = lib.buildargs()
        args = parser.parse_args(["--thumb-only", "project1"])
        assert args.thumb_only is True


class TestCheckFileReadable:
    def test_exists_and_readable(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            f.flush()
            try:
                result = lib.check_file_readable(f.name)
                assert result is True
            finally:
                os.unlink(f.name)

    def test_not_exists(self):
        result = lib.check_file_readable("/nonexistent/path/to/file.txt")
        assert result is False


class TestCheckDirWritable:
    def test_exists_and_writable(self, tmp_path):
        result = lib.check_dir_writable(str(tmp_path))
        assert result is True

    def test_not_exists(self):
        result = lib.check_dir_writable("/nonexistent/path/to/dir")
        assert result is False


class TestEnsureDirWritable:
    def test_creates_new_dir(self, tmp_path):
        new_dir = tmp_path / "new" / "nested" / "dir"
        result = lib.ensure_dir_writable(str(new_dir))
        assert result is True
        assert os.path.isdir(str(new_dir))

    def test_handles_existing_dir(self, tmp_path):
        result = lib.ensure_dir_writable(str(tmp_path))
        assert result is True


class TestCheckMountedAndWritable:
    def test_exists_and_writable_no_mount_check(self, tmp_path):
        result = lib.check_mounted_and_writable(str(tmp_path), check_mount=False)
        assert result is True

    def test_not_exists(self):
        result = lib.check_mounted_and_writable("/nonexistent/path")
        assert result is False


class TestBuildRsyncCmd:
    def test_base_command(self):
        cmd = lib.build_rsync_cmd("/path/to/excludes.txt", dry_run=False, verbose=False)
        assert "rsync" in cmd
        assert "--recursive" in cmd
        assert "--human-readable" in cmd
        assert "--chmod=Dg=rwxs,Fgu=rw,Fo=r" in cmd
        assert "--update" in cmd
        assert "--backup" in cmd
        assert "--exclude-from=/path/to/excludes.txt" in cmd
        assert "--mkpath" in cmd

    def test_dry_run_flag(self):
        cmd = lib.build_rsync_cmd("/path/to/excludes.txt", dry_run=True, verbose=False)
        assert "--dry-run" in cmd

    def test_no_dry_run_flag(self):
        cmd = lib.build_rsync_cmd("/path/to/excludes.txt", dry_run=False, verbose=False)
        assert "--dry-run" not in cmd


class TestValidateProject:
    def test_existing_readable_project(self):
        result = lib.validate_project("empyre")
        assert result is True

    def test_not_exists(self, tmp_path):
        with patch.object(lib, "SOURCE_BASE", str(tmp_path)):
            result = lib.validate_project("nonexistent")
            assert result is False


class TestValidateExcludes:
    def test_readable_excludes_file(self):
        result = lib.validate_excludes(lib.DEFAULT_EXCLUDES)
        assert result is True

    def test_not_readable(self):
        result = lib.validate_excludes("/nonexistent/excludes.txt")
        assert result is False


class TestPrepareStaging:
    def test_creates_staging_dir(self, tmp_path):
        staging_path = lib.prepare_staging(str(tmp_path), "testproject")
        expected = os.path.join(str(tmp_path), "work", "testproject")
        assert staging_path == expected
        assert os.path.isdir(expected)


class TestValidateBackupdevice:
    def test_writable_no_mount_check(self, tmp_path):
        result = lib.validate_backupdevice(str(tmp_path), check_mount=False)
        assert result is True

    def test_not_writable(self, tmp_path):
        os.chmod(str(tmp_path), 0o444)
        try:
            result = lib.validate_backupdevice(str(tmp_path), check_mount=False)
            assert result is False
        finally:
            os.chmod(str(tmp_path), 0o755)


class TestRunRsync:
    @patch("backuptools.lib.subprocess.run")
    def test_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        mock_args = MagicMock()
        mock_args.verbose = False
        mock_args.debug = False

        result = lib.run_rsync(mock_args, ["rsync", "src/", "dest/"], "src/", "dest/")
        assert result == 0
        mock_run.assert_called_once()

    @patch("backuptools.lib.subprocess.run")
    def test_failure(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "error message"
        mock_run.return_value = mock_result

        mock_args = MagicMock()
        mock_args.verbose = False
        mock_args.debug = False

        result = lib.run_rsync(mock_args, ["rsync", "src/", "dest/"], "src/", "dest/")
        assert result == 1

    @patch("backuptools.lib.subprocess.run")
    def test_exception(self, mock_run):
        mock_run.side_effect = Exception("rsync exception")

        mock_args = MagicMock()
        mock_args.verbose = False
        mock_args.debug = False

        result = lib.run_rsync(mock_args, ["rsync", "src/", "dest/"], "src/", "dest/")
        assert result == -1
