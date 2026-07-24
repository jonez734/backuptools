from bbsengine6 import io
from bbsengine6.common import safe_path

from . import lib


def buildargs(args=None, **kwargs):
    return lib.buildargs(args, **kwargs)


def init(args, **kwargs) -> bool:
    return True


def access(args, op, **kwargs) -> bool:
    return True


def main(args=None, **kwargs):
    if args is None:
        parser = buildargs()
        args = parser.parse_args()

    if not lib.validate_excludes(args.excludes):
        return 1

    projects = [p.rstrip("/") for p in args.projects]

    if not args.thumb_only:
        for project in projects:
            if not lib.validate_project(project):
                return 1
    else:
        for project in projects:
            if not lib.validate_project(project):
                io.echo(
                    f"{{labelcolor}}project not found: {{valuecolor}}{project}{{labelcolor}} (required for thumb-only mode)",
                    level="error",
                )
                return 1

    io.echo(f"{{labelcolor}}staging:{{valuecolor}} {args.staging}")
    io.echo(f"{{labelcolor}}backup device:{{valuecolor}} {args.backupdevice}{{/all}}")

    rsync_cmd = lib.build_rsync_cmd(args.excludes, args.dry_run, args.verbose)

    if not args.thumb_only:
        for project in projects:
            io.echo(f"{{labelcolor}}backing up:{{valuecolor}} {project}{{/all}}")

            staging_project = lib.prepare_staging(args.staging, project)
            if staging_project is None:
                return 1

            source_path = safe_path(lib.SOURCE_BASE, project)
            staging_work = safe_path(args.staging, "work")

            io.echo(f"{{labelcolor}}rsync to staging:{{valuecolor}} {source_path} {{labelcolor}}->{{valuecolor}} {staging_work}/{{/all}}")
            if args.verbose:
                io.echo(f"{{labelcolor}}rsync cmd:{{valuecolor}} {' '.join(rsync_cmd + [source_path, staging_work + '/'])}{{/all}}")
            res = lib.run_rsync(args, rsync_cmd, source_path, staging_work + "/")
            if res != 0:
                io.echo(f"rsync to staging failed for {project}", level="error")
                return 1

    if args.stage_only:
        io.echo("stage-only mode: skipping backup device sync")
        return 0

    if not lib.validate_backupdevice(args.backupdevice, not args.no_mount_check):
        return 1

    staging_work = safe_path(args.staging, "work")
    backup_work = safe_path(args.backupdevice)

    if args.thumb_only:
        io.echo("thumb-only mode: syncing staging to backup device")

    io.echo(f"{{labelcolor}}rsync to backup:{{valuecolor}} {staging_work} {{labelcolor}}->{{valuecolor}} {backup_work}/{{/all}}")
    if args.verbose:
        io.echo(f"{{labelcolor}}rsync cmd:{{valuecolor}} {' '.join(rsync_cmd + [staging_work, backup_work + '/'])}{{/all}}")
    res = lib.run_rsync(args, rsync_cmd, staging_work, backup_work + "/")
    if res != 0:
        io.echo("rsync to backup device failed", level="error")
        return 1

    io.echo("backup complete", level="ok")
    return 0
