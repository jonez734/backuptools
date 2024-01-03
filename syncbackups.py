#!/usr/bin/env python

import os, sys, argparse
from argparse import ArgumentParser

from bbsengine6 import io

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args=None):
    parser = ArgumentParser(usage="usage: %prog [options]")
    parser.add_argument("--verbose", dest="verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_argument("--dry-run", dest="dryrun", default=False, action="store_true", help="run %prog in dry-run mode")
#    parser.add_argument("--no-dry-run", dest="dryrun", default=False, action="store_false", help="run %prog in no dry-run mode")
    parser.add_argument("--progress", dest="progress", default=sys.stdout.isatty(), action="store_true", help="show file transfer progress (default: %s)" % (sys.stdout.isatty()))
    parser.add_argument("--debug", dest="debug", default=True, action="store_true", help="run %prog in debug mode")
    parser.add_argument("--mode", dest="mode", default=None, action="store", help="specify mode for backups sync (thumbdrive, projects, or falcon)")
    parser.add_argument("--thumbdrivebasedir", dest="thumbdrivebasedir", default=THUMBDRIVE, action="store", help="basedir of thumbdrive")
    parser.add_argument("--delete-after", dest="deleteafter", default=False, action="store_true", help="add --delete-after to rsync command line (default: %s)")

    return parser

def buildcmd(opts, args):
    cmd = []
    cmd.append("rsync")
    cmd.append("--recursive")
    cmd.append("--human-readable")
    cmd.append("--chmod=Dg=rwxs,Fgu=rw,Fo=r")
#    cmd.append("--group")
    cmd.append("--update --backup")
    cmd.append("--rsh=ssh") #  --delete-after --links")
    cmd.append("--exclude '.~lock*' --exclude '*~'")
    cmd.append("--mkpath")
#    cmd.append(" --exclude .git")
    if opts.verbose is True:
        cmd.append("--verbose")
    if opts.dryrun is True:
        cmd.append("--dry-run")
    if sys.stdout.isatty() is True:
        cmd.append("--progress")
    return "%s %s" % (" ".join(cmd), args)

THUMBDRIVE = "/run/media/jam/AEAB-CF37/" # 6F6A-A171

def run(args, cmd):
    if args.dryrun is True:
        io.echo(f"** dry run ** {cmd}")
        res = True
    else:
        io.echo(cmd, level="debug")
        res = os.system(cmd)
    return res

def main():

    parser = buildargs()
    args = parser.parse_args()

    # sync from falcon to cyclops as "backups"
    # sync from cyclops to falcon as "backups"
    # sync from cyclops to thumbdrive if mounted as "jam"
    # sync ~jam/projects/ to /srv/backups on cyclops as "jam"
    cmds = []
    if args.mode is None:
        io.echo("specify --mode!", level="error")
        return -1
#    elif args.mode == "cyclops-pgdump-thumbdrive":
#        io.echo("syncing cyclops pgdumps to thumbdrive")
#        cmds.append(f"/srv/backups/cyclops/pgdumps/*.pgdump {args.thumbdrivebasedir}/backups/cyclops/pgdumps/")
#    elif opts.mode == "falcon-pgdump-thumbdrive":
#        io.echo("syncing *falcon*.pgdump to thumbdrive")
#        cmds.append("/srv/backups/falcon/pgdumps/*.pgdump %s/backups/falcon/pgdumps/" % (opts.thumbdrive))

    elif args.mode == "thumbdrive":
        if os.path.isdir(args.thumbdrivebasedir) and os.access(args.thumbdrivebasedir, os.W_OK):
             cmds.append(f"/srv/backups/ {args.thumbdrivebasedir}")
        else:
            io.echo("thumbdrive not mounted or mounted read-only", level="error")
            return -1
    elif args.mode == "projects":
        # rsync --verbose --recursive --copy-links --exclude .git --exclude .svn ~jam/projects /run/media/jam/6F6A-A171/
        cmds.append("/home/jam/projects /srv/backups/")
#    elif opts.mode == "falcon":
#        cmds.append("backups@falcon:/srv/backups/falcon /srv/backups/")
#    elif args.mode == "cyclops":
#        cmds.append("/srv/backups/cyclops backups@falcon:/srv/backups/")
    elif args.mode == "vhosts":
        for host in ("falcon", "merlin"): #, "copper"):
            cmds.append(f"{host}:/srv/www/vhosts /srv/backups/{host}/")
    elif args.mode == "home":
        cmds.append("~jam/Pictures /srv/backups/")
        cmds.append("~jam/.ssh/ /srv/backups/ssh/")
        cmds.append("~jam/.gnupg/ /srv/backups/gnupg/")
    elif args.mode == "repo":
#        cmds.append("backups@falcon:/srv/repo /srv/backups/falcon/")
        cmds.append("/srv/repo /srv/backups/")
    for c in cmds:
        cmd = buildcmd(args, c)
        res = run(args, cmd)
        if res < 0:
            return res
    return

if __name__ == "__main__":
    sys.exit(main())
