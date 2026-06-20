import os
import sys
from argparse import Namespace
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import backuptools.main as main_module


pytestmark = pytest.mark.unit


class TestMainBuildargs:
    def test_returns_argumentparser(self):
        parser = main_module.buildargs()
        assert parser is not None


class TestMainInit:
    def test_returns_true(self):
        result = main_module.init(None)
        assert result is True


class TestMainAccess:
    def test_returns_true(self):
        result = main_module.access(None, "read")
        assert result is True


class TestMainFull:
    @patch("backuptools.main.lib.validate_excludes")
    @patch("backuptools.main.lib.validate_project")
    @patch("backuptools.main.lib.prepare_staging")
    @patch("backuptools.main.lib.run_rsync")
    @patch("backuptools.main.lib.validate_backupdevice")
    @patch("backuptools.main.lib.build_rsync_cmd")
    def test_full_backup_success(
        self,
        mock_build_rsync_cmd,
        mock_validate_backupdevice,
        mock_run_rsync,
        mock_prepare_staging,
        mock_validate_project,
        mock_validate_excludes,
    ):
        mock_validate_excludes.return_value = True
        mock_validate_project.return_value = True
        mock_prepare_staging.return_value = "/staging/work/project"
        mock_build_rsync_cmd.return_value = ["rsync"]
        mock_run_rsync.return_value = 0
        mock_validate_backupdevice.return_value = True

        args = Namespace(
            projects=["project1"],
            staging="/staging/",
            backupdevice="/backupdevice/",
            excludes="/excludes.txt",
            dry_run=False,
            verbose=False,
            no_mount_check=False,
            stage_only=False,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 0
        mock_validate_excludes.assert_called_once()
        mock_validate_project.assert_called_once()
        mock_prepare_staging.assert_called_once()
        mock_run_rsync.assert_called()
        mock_validate_backupdevice.assert_called_once()

    @patch("backuptools.main.lib.validate_excludes")
    def test_excludes_validation_fails(self, mock_validate_excludes):
        mock_validate_excludes.return_value = False

        args = Namespace(
            projects=["project1"],
            staging="/staging/",
            backupdevice="/backupdevice/",
            excludes="/excludes.txt",
            dry_run=False,
            verbose=False,
            no_mount_check=False,
            stage_only=False,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 1
        mock_validate_excludes.assert_called_once()

    @patch("backuptools.main.lib.validate_excludes")
    @patch("backuptools.main.lib.validate_project")
    def test_project_validation_fails(
        self, mock_validate_project, mock_validate_excludes
    ):
        mock_validate_excludes.return_value = True
        mock_validate_project.return_value = False

        args = Namespace(
            projects=["nonexistent"],
            staging="/staging/",
            backupdevice="/backupdevice/",
            excludes="/excludes.txt",
            dry_run=False,
            verbose=False,
            no_mount_check=False,
            stage_only=False,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 1

    @patch("backuptools.main.lib.validate_excludes")
    @patch("backuptools.main.lib.validate_project")
    @patch("backuptools.main.lib.prepare_staging")
    @patch("backuptools.main.lib.run_rsync")
    @patch("backuptools.main.lib.build_rsync_cmd")
    def test_stage_only_mode(
        self,
        mock_build_rsync_cmd,
        mock_run_rsync,
        mock_prepare_staging,
        mock_validate_project,
        mock_validate_excludes,
    ):
        mock_validate_excludes.return_value = True
        mock_validate_project.return_value = True
        mock_prepare_staging.return_value = "/staging/work/project"
        mock_build_rsync_cmd.return_value = ["rsync"]
        mock_run_rsync.return_value = 0

        args = Namespace(
            projects=["project1"],
            staging="/staging/",
            backupdevice="/backupdevice/",
            excludes="/excludes.txt",
            dry_run=False,
            verbose=False,
            no_mount_check=False,
            stage_only=True,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 0
        mock_run_rsync.assert_called_once()


class TestThumbOnly:
    @patch("backuptools.main.lib.validate_excludes")
    @patch("backuptools.main.lib.validate_project")
    @patch("backuptools.main.lib.run_rsync")
    @patch("backuptools.main.lib.validate_backupdevice")
    @patch("backuptools.main.lib.build_rsync_cmd")
    def test_thumb_only_mode(
        self,
        mock_build_rsync_cmd,
        mock_validate_backupdevice,
        mock_run_rsync,
        mock_validate_project,
        mock_validate_excludes,
    ):
        mock_validate_excludes.return_value = True
        mock_validate_project.return_value = True
        mock_build_rsync_cmd.return_value = ["rsync"]
        mock_run_rsync.return_value = 0
        mock_validate_backupdevice.return_value = True

        args = Namespace(
            projects=["project1"],
            staging="/staging/",
            backupdevice="/backupdevice/",
            excludes="/excludes.txt",
            dry_run=False,
            verbose=False,
            no_mount_check=False,
            stage_only=False,
            thumb_only=True,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 0
        mock_validate_project.assert_called_once()
        mock_validate_excludes.assert_called_once()
        mock_run_rsync.assert_called_once()
        mock_validate_backupdevice.assert_called_once()
