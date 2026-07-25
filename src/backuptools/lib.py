import os
import re
import subprocess
import sys
from argparse import ArgumentParser

from bbsengine6 import io, module
from bbsengine6.common import safe_path

from backuptools._version import __version__


def _get_default_excludes() -> str:
    return safe_path(os.path.dirname(__file__), "rsync-excludes.txt")


DEFAULT_EXCLUDES = _get_default_excludes()
DEFAULT_STAGING = "/srv/backups/"
DEFAULT_BACKUPDEVICE = "/run/media/jam/BEA6-BBCE/"
DEFAULT_DATABASE_SOURCE = "/srv/backups/database"
DATABASE_RE = re.compile(r"^(database|minotaur)$")
SOURCE_BASE = "/home/opencode/data/work"

PACKAGENAME = "backuptools"


def runmodule(args, modulename, **kwargs):
    return module.runmodule(args, f"{PACKAGENAME}.{modulename}", **kwargs)


def buildargs(args=None, **kwargs):
    parser = ArgumentParser(usage="usage: backup.py [options] project [project ...]")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--debug", action="store_true", help="debug mode")
    parser.add_argument("projects", nargs="+", help="project names to backup")
    parser.add_argument(
        "--staging",
        default=DEFAULT_STAGING,
        help="staging directory base",
    )
    parser.add_argument(
        "--backupdevice",
        default=DEFAULT_BACKUPDEVICE,
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
    parser.add_argument(
        "--stage-only",
        action="store_true",
        help="only copy to staging, skip backup device sync",
    )
    parser.add_argument(
        "--thumb-only",
        action="store_true",
        help="only sync staging to backup device, skip source to staging",
    )
    parser.add_argument(
        "--database-source",
        default=DEFAULT_DATABASE_SOURCE,
        help="source path for database backups (default: /srv/backups/database)",
    )
    return parser


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
        "--xattrs",
        "--update",
        "--backup",
        f"--exclude-from={excludes_file}",
        "--mkpath",
    ]
    if dry_run:
        cmd.append("--dry-run")
    if verbose:
        cmd.append("--progress")
        cmd.append("--verbose")
    return cmd


def run_rsync(args, cmd: list, source: str, dest: str) -> int:
    full_cmd = cmd + [source, dest]
    if getattr(args, "debug", False):
        io.echo(f"run_rsync.100: {full_cmd=}", level="debug")
    try:
        verbose = getattr(args, "verbose", False)
        if verbose:
            sys.stdout.flush()
            sys.stderr.flush()
            proc = subprocess.Popen(full_cmd, stdout=1, stderr=2)
            return proc.wait()
        else:
            result = subprocess.run(full_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                io.echo(f"rsync failed: {result.stderr}", level="error")
            return result.returncode
    except Exception as e:
        io.echo_traceback(f"rsync exception: {e}")
        return -1


def validate_project(project: str) -> bool:
    project_path = safe_path(SOURCE_BASE, project)
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
    staging_path = safe_path(staging_base, "work", project)
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


def validate_database_source(source: str) -> bool:
    if not os.path.isdir(source):
        io.echo(f"database source not found: {source}", level="error")
        return False
    if not os.access(source, os.R_OK):
        io.echo(f"database source not readable: {source}", level="error")
        return False
    return True
