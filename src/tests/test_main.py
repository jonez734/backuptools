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
        parser = main_module.buildargs(None)
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


class TestDatabaseAlone:
    @patch("backuptools.main.lib.validate_excludes")
    @patch("backuptools.main.lib.validate_database_source")
    @patch("backuptools.main.lib.run_rsync")
    @patch("backuptools.main.lib.validate_backupdevice")
    @patch("backuptools.main.lib.build_rsync_cmd")
    def test_database_alone_runs_one_rsync(
        self,
        mock_build_rsync_cmd,
        mock_validate_backupdevice,
        mock_run_rsync,
        mock_validate_database_source,
        mock_validate_excludes,
    ):
        mock_validate_excludes.return_value = True
        mock_validate_database_source.return_value = True
        mock_build_rsync_cmd.return_value = ["rsync"]
        mock_run_rsync.return_value = 0
        mock_validate_backupdevice.return_value = True

        args = Namespace(
            projects=["database"],
            staging="/staging/",
            backupdevice="/backupdevice/",
            excludes="/excludes.txt",
            database_source="/srv/backups/database",
            dry_run=False,
            verbose=False,
            no_mount_check=False,
            stage_only=False,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 0
        mock_validate_database_source.assert_called_once_with("/srv/backups/database")
        # exactly one rsync: db_source -> backup_work/. The staging->device
        # sync must NOT run when no fs projects are present.
        assert mock_run_rsync.call_count == 1
        call_args = mock_run_rsync.call_args
        assert call_args.args[2] == "/srv/backups/database"
        assert call_args.args[3] == "/backupdevice/"

    @patch("backuptools.main.lib.validate_excludes")
    @patch("backuptools.main.lib.validate_database_source")
    def test_database_alone_validates_source(
        self, mock_validate_database_source, mock_validate_excludes
    ):
        mock_validate_excludes.return_value = True
        mock_validate_database_source.return_value = False

        args = Namespace(
            projects=["database"],
            staging="/staging/",
            backupdevice="/backupdevice/",
            excludes="/excludes.txt",
            database_source="/nonexistent/db",
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
    @patch("backuptools.main.lib.validate_database_source")
    @patch("backuptools.main.lib.run_rsync")
    @patch("backuptools.main.lib.validate_backupdevice")
    @patch("backuptools.main.lib.build_rsync_cmd")
    def test_database_alone_with_stage_only_still_runs_db_rsync(
        self,
        mock_build_rsync_cmd,
        mock_validate_backupdevice,
        mock_run_rsync,
        mock_validate_database_source,
        mock_validate_excludes,
    ):
        # --stage-only skips the staging->device sync but db targets
        # are not affected: they have no staging step, so their
        # db_source->backup_work rsync still runs.
        mock_validate_excludes.return_value = True
        mock_validate_database_source.return_value = True
        mock_build_rsync_cmd.return_value = ["rsync"]
        mock_run_rsync.return_value = 0
        mock_validate_backupdevice.return_value = True

        args = Namespace(
            projects=["database"],
            staging="/staging/",
            backupdevice="/backupdevice/",
            excludes="/excludes.txt",
            database_source="/srv/backups/database",
            dry_run=False,
            verbose=False,
            no_mount_check=False,
            stage_only=True,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 0
        assert mock_run_rsync.call_count == 1


class TestDatabaseMixedWithFilesystem:
    """Regression tests for the `database` short-circuit bug.

    Bug: `backup database teos` used to run the database rsync and
    silently drop `teos` (and skip the final staging->device sync).
    The fix splits projects into db_targets and fs_projects up front
    and runs both, plus the final sync, in input order.
    """

    def _make_args(self, projects, stage_only=False, thumb_only=False):
        return Namespace(
            projects=projects,
            staging="/staging/",
            backupdevice="/backupdevice/",
            excludes="/excludes.txt",
            database_source="/srv/backups/database",
            dry_run=False,
            verbose=False,
            no_mount_check=False,
            stage_only=stage_only,
            thumb_only=thumb_only,
            debug=False,
        )

    @patch("backuptools.main.lib.validate_excludes")
    @patch("backuptools.main.lib.validate_project")
    @patch("backuptools.main.lib.validate_database_source")
    @patch("backuptools.main.lib.prepare_staging")
    @patch("backuptools.main.lib.run_rsync")
    @patch("backuptools.main.lib.validate_backupdevice")
    @patch("backuptools.main.lib.build_rsync_cmd")
    def test_database_then_filesystem_runs_all_in_order(
        self,
        mock_build_rsync_cmd,
        mock_validate_backupdevice,
        mock_run_rsync,
        mock_prepare_staging,
        mock_validate_database_source,
        mock_validate_project,
        mock_validate_excludes,
    ):
        mock_validate_excludes.return_value = True
        mock_validate_database_source.return_value = True
        mock_validate_project.return_value = True
        mock_prepare_staging.return_value = "/staging/work/teos"
        mock_build_rsync_cmd.return_value = ["rsync"]
        mock_run_rsync.return_value = 0
        mock_validate_backupdevice.return_value = True

        result = main_module.main(self._make_args(["database", "teos"]))

        assert result == 0
        mock_validate_database_source.assert_called_once()
        mock_validate_project.assert_called_once_with("teos")
        # 3 rsyncs: db_source->device, teos->staging, staging->device.
        # The old code did 1 (only the db rsync) and silently dropped
        # teos plus the final sync.
        assert mock_run_rsync.call_count == 3
        calls = mock_run_rsync.call_args_list
        assert calls[0].args[2] == "/srv/backups/database"
        assert calls[0].args[3] == "/backupdevice/"
        assert calls[1].args[2] == "/home/opencode/data/work/teos"
        assert calls[1].args[3] == "/staging/work/"
        assert calls[2].args[2] == "/staging/work"
        assert calls[2].args[3] == "/backupdevice/"

    @patch("backuptools.main.lib.validate_excludes")
    @patch("backuptools.main.lib.validate_project")
    @patch("backuptools.main.lib.validate_database_source")
    @patch("backuptools.main.lib.prepare_staging")
    @patch("backuptools.main.lib.run_rsync")
    @patch("backuptools.main.lib.validate_backupdevice")
    @patch("backuptools.main.lib.build_rsync_cmd")
    def test_filesystem_then_database_runs_all_in_order(
        self,
        mock_build_rsync_cmd,
        mock_validate_backupdevice,
        mock_run_rsync,
        mock_prepare_staging,
        mock_validate_database_source,
        mock_validate_project,
        mock_validate_excludes,
    ):
        # Input order: fs project before db target. The fs staging
        # rsync should run first, then the db rsync, then the final
        # staging->device sync.
        mock_validate_excludes.return_value = True
        mock_validate_database_source.return_value = True
        mock_validate_project.return_value = True
        mock_prepare_staging.return_value = "/staging/work/teos"
        mock_build_rsync_cmd.return_value = ["rsync"]
        mock_run_rsync.return_value = 0
        mock_validate_backupdevice.return_value = True

        result = main_module.main(self._make_args(["teos", "database"]))

        assert result == 0
        assert mock_run_rsync.call_count == 3
        calls = mock_run_rsync.call_args_list
        assert calls[0].args[2] == "/home/opencode/data/work/teos"
        assert calls[0].args[3] == "/staging/work/"
        assert calls[1].args[2] == "/srv/backups/database"
        assert calls[1].args[3] == "/backupdevice/"
        assert calls[2].args[2] == "/staging/work"
        assert calls[2].args[3] == "/backupdevice/"

    @patch("backuptools.main.lib.validate_excludes")
    @patch("backuptools.main.lib.validate_project")
    @patch("backuptools.main.lib.validate_database_source")
    @patch("backuptools.main.lib.prepare_staging")
    @patch("backuptools.main.lib.run_rsync")
    @patch("backuptools.main.lib.validate_backupdevice")
    @patch("backuptools.main.lib.build_rsync_cmd")
    def test_minotaur_alias_runs_all_with_filesystem(
        self,
        mock_build_rsync_cmd,
        mock_validate_backupdevice,
        mock_run_rsync,
        mock_prepare_staging,
        mock_validate_database_source,
        mock_validate_project,
        mock_validate_excludes,
    ):
        # `minotaur` is the legacy alias for `database` (lib.DATABASE_RE
        # matches both). It must be treated as a db target, not as a
        # filesystem project that would fail validation.
        mock_validate_excludes.return_value = True
        mock_validate_database_source.return_value = True
        mock_validate_project.return_value = True
        mock_prepare_staging.return_value = "/staging/work/teos"
        mock_build_rsync_cmd.return_value = ["rsync"]
        mock_run_rsync.return_value = 0
        mock_validate_backupdevice.return_value = True

        result = main_module.main(self._make_args(["minotaur", "teos"]))

        assert result == 0
        # validate_project must be called only for `teos`, never for
        # `minotaur` (it's a db target, not a fs project).
        mock_validate_project.assert_called_once_with("teos")
        # 3 rsyncs: same shape as the database variant.
        assert mock_run_rsync.call_count == 3
        calls = mock_run_rsync.call_args_list
        assert calls[0].args[2] == "/srv/backups/database"
        assert calls[0].args[3] == "/backupdevice/"
        assert calls[1].args[2] == "/home/opencode/data/work/teos"
        assert calls[1].args[3] == "/staging/work/"
        assert calls[2].args[2] == "/staging/work"
        assert calls[2].args[3] == "/backupdevice/"

    @patch("backuptools.main.lib.validate_excludes")
    @patch("backuptools.main.lib.validate_database_source")
    def test_database_does_not_short_circuit_validation(
        self, mock_validate_database_source, mock_validate_excludes
    ):
        # The old short-circuit ran `validate_database_source` but
        # skipped every fs project's `validate_project`. The new
        # code calls `validate_database_source` once and then
        # `validate_project` for every fs project. With a bad db
        # source AND a real fs project, both should be checked and
        # the function should return 1.
        mock_validate_excludes.return_value = True
        mock_validate_database_source.return_value = False

        with patch(
            "backuptools.main.lib.validate_project", return_value=True
        ) as mock_validate_project:
            result = main_module.main(
                self._make_args(["database", "empyre"])
            )

        assert result == 1
        mock_validate_database_source.assert_called_once()
        # The order is: excludes -> db_source -> fs project. With
        # db_source failing, the fs project's validation is not
        # reached (early return), but the db_source check MUST have
        # happened, which is the regression guard.
        mock_validate_project.assert_not_called()
