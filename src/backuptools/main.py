from bbsengine6 import io

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
                    f"project not found: {project} (required for thumb-only mode)",
                    level="error",
                )
                return 1

    io.echo(f"staging: {args.staging}")
    io.echo(f"backup device: {args.backupdevice}")

    rsync_cmd = lib.build_rsync_cmd(args.excludes, args.dry_run, args.verbose)

    if not args.thumb_only:
        for project in projects:
            io.echo(f"backing up: {project}")

            staging_project = lib.prepare_staging(args.staging, project)
            if staging_project is None:
                return 1

            source_path = lib.SOURCE_BASE + "/" + project
            staging_work = args.staging + "work"

            io.echo(f"rsync to staging: {source_path} -> {staging_work}")
            res = lib.run_rsync(rsync_cmd, source_path, staging_work)
            if res != 0:
                io.echo(f"rsync to staging failed for {project}", level="error")
                return 1

    if args.stage_only:
        io.echo("stage-only mode: skipping backup device sync")
        return 0

    if not lib.validate_backupdevice(args.backupdevice, not args.no_mount_check):
        return 1

    staging_work = args.staging + "work"
    backup_work = args.backupdevice + "work"

    if args.thumb_only:
        io.echo(f"thumb-only mode: syncing staging to backup device")

    io.echo(f"rsync to backup: {staging_work} -> {backup_work}")
    res = lib.run_rsync(rsync_cmd, staging_work + "/", backup_work + "/")
    if res != 0:
        io.echo("rsync to backup device failed", level="error")
        return 1

    io.echo("backup complete")
    return 0
