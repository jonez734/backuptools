import os
import shutil
import subprocess
import tempfile
from argparse import Namespace

import pytest

import backuptools.main as main_module
import backuptools.lib as lib


pytestmark = pytest.mark.unit


def dirs_equal(dir1: str, dir2: str) -> bool:
    result = subprocess.run(
        ["diff", "-rq", dir1, dir2],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


class TestRealBackup:
    @pytest.fixture(autouse=True)
    def clean_temp_dirs(self, tmp_path):
        pass

    @pytest.fixture
    def temp_dirs(self):
        staging = tempfile.mkdtemp(prefix="backup-staging-")
        backup = tempfile.mkdtemp(prefix="backup-device-")
        yield staging, backup
        import shutil
        import glob

        for d in glob.glob("/tmp/backup-staging-*"):
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except:
                    pass
        for d in glob.glob("/tmp/backup-device-*"):
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except:
                    pass

    def test_real_backup_to_staging(self, temp_dirs):
        staging, backup = temp_dirs

        args = Namespace(
            projects=["backuptools"],
            staging=staging,
            backupdevice=backup,
            excludes=lib.DEFAULT_EXCLUDES,
            dry_run=False,
            verbose=True,
            no_mount_check=True,
            stage_only=True,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 0

        work_dir = os.path.join(staging, "work")
        assert os.path.isdir(work_dir), f"Expected {work_dir} to exist"

        files = os.listdir(work_dir)
        assert "backuptools" in files, (
            f"Expected backuptools dir in {work_dir}, got {files}"
        )

    def test_real_full_backup(self, temp_dirs):
        staging, backup = temp_dirs

        args = Namespace(
            projects=["backuptools"],
            staging=staging,
            backupdevice=backup,
            excludes=lib.DEFAULT_EXCLUDES,
            dry_run=False,
            verbose=True,
            no_mount_check=True,
            stage_only=False,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 0

        staging_work = os.path.join(staging, "work")
        assert os.path.isdir(staging_work), f"Expected {staging_work} to exist"

        backup_contents = os.listdir(backup)
        assert "work" in backup_contents, (
            f"Expected work dir in {backup}, got {backup_contents}"
        )

    def test_staging_and_backup_are_equal(self, temp_dirs):
        staging, backup = temp_dirs

        args = Namespace(
            projects=["backuptools"],
            staging=staging,
            backupdevice=backup,
            excludes=lib.DEFAULT_EXCLUDES,
            dry_run=False,
            verbose=True,
            no_mount_check=True,
            stage_only=False,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)
        assert result == 0

        staging_work = os.path.join(staging, "work", "backuptools")
        assert os.path.isdir(staging_work)

        backup_work = os.path.join(backup, "work", "backuptools")
        assert os.path.isdir(backup_work)

        assert dirs_equal(staging_work, backup_work), (
            "Staging and backup should be identical"
        )

    def test_dry_run_no_copy(self, temp_dirs):
        staging, backup = temp_dirs

        args = Namespace(
            projects=["backuptools"],
            staging=staging,
            backupdevice=backup,
            excludes=lib.DEFAULT_EXCLUDES,
            dry_run=True,
            verbose=True,
            no_mount_check=True,
            stage_only=True,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 0

        work_dir = os.path.join(staging, "work")
        project_dir = os.path.join(work_dir, "backuptools")
        if os.path.exists(project_dir):
            files = os.listdir(project_dir)
            assert len(files) == 0, (
                f"Expected no files in {project_dir} with --dry-run, got {files}"
            )

    def test_thumb_only_mode(self, temp_dirs):
        staging, backup = temp_dirs

        args_stage = Namespace(
            projects=["backuptools"],
            staging=staging,
            backupdevice=backup,
            excludes=lib.DEFAULT_EXCLUDES,
            dry_run=False,
            verbose=True,
            no_mount_check=True,
            stage_only=True,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args_stage)
        assert result == 0

        staging_work = os.path.join(staging, "work")
        assert os.path.isdir(staging_work)

        args_thumb = Namespace(
            projects=["backuptools"],
            staging=staging,
            backupdevice=backup,
            excludes=lib.DEFAULT_EXCLUDES,
            dry_run=False,
            verbose=True,
            no_mount_check=True,
            stage_only=False,
            thumb_only=True,
            debug=False,
        )

        result = main_module.main(args_thumb)

        assert result == 0

        backup_contents = os.listdir(backup)
        assert "work" in backup_contents, (
            f"Expected work dir in {backup}, got {backup_contents}"
        )


class TestBackupBbsengine6:
    @pytest.fixture
    def temp_dirs(self):
        staging = tempfile.mkdtemp(prefix="backup-staging-")
        backup = tempfile.mkdtemp(prefix="backup-device-")
        yield staging, backup
        import shutil
        import glob

        for d in glob.glob("/tmp/backup-staging-*"):
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except:
                    pass
        for d in glob.glob("/tmp/backup-device-*"):
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except:
                    pass

    def test_backup_bbsengine6_to_staging(self, temp_dirs):
        staging, backup = temp_dirs

        args = Namespace(
            projects=["bbsengine6"],
            staging=staging,
            backupdevice=backup,
            excludes=lib.DEFAULT_EXCLUDES,
            dry_run=False,
            verbose=True,
            no_mount_check=True,
            stage_only=True,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 0

        work_dir = os.path.join(staging, "work")
        assert os.path.isdir(work_dir), f"Expected {work_dir} to exist"

        files = os.listdir(work_dir)
        assert "bbsengine6" in files, (
            f"Expected bbsengine6 dir in {work_dir}, got {files}"
        )

    def test_backup_bbsengine6_full_backup(self, temp_dirs):
        staging, backup = temp_dirs

        args = Namespace(
            projects=["bbsengine6"],
            staging=staging,
            backupdevice=backup,
            excludes=lib.DEFAULT_EXCLUDES,
            dry_run=False,
            verbose=True,
            no_mount_check=True,
            stage_only=False,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 0

        staging_work = os.path.join(staging, "work")
        assert os.path.isdir(staging_work), f"Expected {staging_work} to exist"

        backup_contents = os.listdir(backup)
        assert "work" in backup_contents, (
            f"Expected work dir in {backup}, got {backup_contents}"
        )

    def test_backup_bbsengine6_staging_and_backup_equal(self, temp_dirs):
        staging, backup = temp_dirs

        args = Namespace(
            projects=["bbsengine6"],
            staging=staging,
            backupdevice=backup,
            excludes=lib.DEFAULT_EXCLUDES,
            dry_run=False,
            verbose=True,
            no_mount_check=True,
            stage_only=False,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)
        assert result == 0

        staging_work = os.path.join(staging, "work", "bbsengine6")
        assert os.path.isdir(staging_work)

        backup_work = os.path.join(backup, "work", "bbsengine6")
        assert os.path.isdir(backup_work)

        assert dirs_equal(staging_work, backup_work), (
            "Staging and backup should be identical"
        )

    def test_backup_bbsengine6_dry_run(self, temp_dirs):
        staging, backup = temp_dirs

        args = Namespace(
            projects=["bbsengine6"],
            staging=staging,
            backupdevice=backup,
            excludes=lib.DEFAULT_EXCLUDES,
            dry_run=True,
            verbose=True,
            no_mount_check=True,
            stage_only=True,
            thumb_only=False,
            debug=False,
        )

        result = main_module.main(args)

        assert result == 0

        work_dir = os.path.join(staging, "work")
        project_dir = os.path.join(work_dir, "bbsengine6")
        if os.path.exists(project_dir):
            files = os.listdir(project_dir)
            assert len(files) == 0, (
                f"Expected no files in {project_dir} with --dry-run, got {files}"
            )
