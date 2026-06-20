#!/usr/bin/env python3
import os
import sys
import subprocess

from argparse import ArgumentParser

from bbsengine6 import io


DEFAULT_EXCLUDES = "/home/opencode/data/work/backuptools/rsync-excludes.txt"
DEFAULT_STAGING = "/srv/backups/"
DEFAULT_BACKUPDEVICE = "/run/media/jam/BEA6-BBCE/"
SOURCE_BASE = "/home/opencode/data/work"


def check_file_readable(path: str) -> bool:
    if not os.path.exists(path):
        return False
    return os.access(path, os.R_OK)


def check_dir_writable(path: str) -> bool:
    if os.path.exists(path):
        return os.access(path, os.W_OK)
    return False


def ensure_dir_writable(path: str) -> bool:
    try:
        os.makedirs(path, exist_ok=True)
        return os.access(path, os.W_OK)
    except Exception:
        return False


def check_mounted_and_writable(path: str, check_mount: bool = True) -> bool:
    if not os.path.exists(path):
        return False
    if check_mount and not os.path.ismount(path):
        return False
    return os.access(path, os.W_OK)


def build_rsync_cmd(
    excludes_file: str, dry_run: bool = False, verbose: bool = True
) -> list:
    cmd = [
        "rsync",
        "--recursive",
        "--human-readable",
        "--chmod=Dg=rwxs,Fgu=rw,Fo=r",
        "--update",
        "--backup",
        "--exclude-from",
        excludes_file,
        "--mkpath",
    ]
    if dry_run:
        cmd.append("--dry-run")
    if verbose and sys.stdout.isatty():
        cmd.append("--progress")
    return cmd


def run_rsync(cmd: list, source: str, dest: str) -> int:
    full_cmd = cmd + [source, dest]
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            io.echo(f"rsync failed: {result.stderr}", level="error")
        return result.returncode
    except Exception as e:
        io.echo_traceback(f"rsync exception: {e}")
        return -1


def validate_project(project: str) -> bool:
    project_path = os.path.join(SOURCE_BASE, project)
    if not os.path.isdir(project_path):
        io.echo(f"project not found: {project_path}", level="error")
        return False
    if not check_file_readable(project_path):
        io.echo(f"project not readable: {project_path}", level="error")
        return False
    return True


def validate_excludes(excludes_file: str) -> bool:
    if not check_file_readable(excludes_file):
        io.echo(f"excludes file not readable: {excludes_file}", level="error")
        return False
    return True


def prepare_staging(staging_base: str, project: str) -> str:
    staging_path = os.path.join(staging_base, "work", project)
    if not ensure_dir_writable(staging_path):
        io.echo(f"staging not writable: {staging_path}", level="error")
        return None
    return staging_path


def validate_backupdevice(backupdevice: str, check_mount: bool = True) -> bool:
    if not check_mounted_and_writable(backupdevice, check_mount):
        io.echo(
            f"backup device not mounted or not writable: {backupdevice}", level="error"
        )
        return False
    return True


def buildargs():
    parser = ArgumentParser(usage="usage: backup.py [options] project [project ...]")
    parser.add_argument("projects", nargs="+", help="project names to backup")
    parser.add_argument(
        "--staging",
        default=DEFAULT_STAGING,
        help="staging directory base",
    )
    parser.add_argument(
        "--backupdevice",
        default=os.getenv("BACKUPDEVICE", DEFAULT_BACKUPDEVICE),
        help="backup device path",
    )
    parser.add_argument(
        "--excludes",
        default=DEFAULT_EXCLUDES,
        help="rsync excludes file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="dry run mode",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="verbose output",
    )
    parser.add_argument(
        "--no-mount-check",
        action="store_true",
        help="skip mount point check for backup device (for testing)",
    )
    return parser


def main():
    parser = buildargs()
    args = parser.parse_args()

    if not validate_excludes(args.excludes):
        return 1

    for project in args.projects:
        if not validate_project(project):
            return 1

    io.echo(f"staging: {args.staging}")
    io.echo(f"backup device: {args.backupdevice}")

    rsync_cmd = build_rsync_cmd(args.excludes, args.dry_run, args.verbose)

    for project in args.projects:
        io.echo(f"backing up: {project}")

        staging_project = prepare_staging(args.staging, project)
        if staging_project is None:
            return 1

        source_path = os.path.join(SOURCE_BASE, project)
        staging_work = os.path.join(args.staging, "work")

        io.echo(f"rsync to staging: {source_path} -> {staging_work}")
        res = run_rsync(rsync_cmd, source_path, staging_work)
        if res != 0:
            io.echo(f"rsync to staging failed for {project}", level="error")
            return 1

    if not validate_backupdevice(args.backupdevice, not args.no_mount_check):
        return 1

    staging_work = os.path.join(args.staging, "work")
    backup_work = os.path.join(args.backupdevice, "work")

    io.echo(f"rsync to backup: {staging_work} -> {backup_work}")
    res = run_rsync(rsync_cmd, staging_work + "/", backup_work + "/")
    if res != 0:
        io.echo("rsync to backup device failed", level="error")
        return 1

    io.echo("backup complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
