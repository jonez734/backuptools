#!/usr/bin/env python

import os, sys
from optparse import OptionParser
import ttyio4 as ttyio

def buildcmd(opts, args):
    cmd = []
    cmd.append("rsync")
    cmd.append("--recursive")
    cmd.append("--human-readable")
    cmd.append("--chmod=Dg=rwxs,Fgu=rw,Fo=r")
    cmd.append("--group")
    cmd.append("--update --backup")
    cmd.append("--rsh=ssh --delete-after --links")
    cmd.append("--exclude '.~lock*' --exclude '*~' --exclude '443'")
    cmd.append("--exclude .svn --exclude .git")
    if opts.verbose is True:
        cmd.append("--verbose")
    if opts.dryrun is True:
        cmd.append("--dry-run")
    if sys.stdout.isatty() is True:
        cmd.append("--progress")
    return "%s %s" % (" ".join(cmd), args)

THUMBDRIVE = "/run/media/jam/6F6A-A171"

def run(opts, cmd):
    if opts.dryrun is True:
        ttyio.echo("** dry run ** "+cmd)
        res = True
    else:
        ttyio.echo(cmd, level="debug")
        res = os.system(cmd)
    return res

def main():
    isatty = sys.stdout.isatty()
    parser = OptionParser(usage="usage: %prog [options] projectid")
    parser.add_option("--verbose", dest="verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_option("--dry-run", dest="dryrun", default=False, action="store_true", help="run %prog in dry-run mode")
#    parser.add_option("--no-dry-run", dest="dryrun", default=False, action="store_false", help="run %prog in no dry-run mode")
    parser.add_option("--progress", dest="progress", default=isatty, action="store_true", help="show file transfer progress (default: %s)" % (sys.stdout.isatty()))
    parser.add_option("--debug", dest="debug", default=True, action="store_true", help="run %prog in debug mode")
    parser.add_option("--mode", dest="mode", default=None, action="store", help="specify mode for backups sync (thumbdrive, projects, or falcon)")
    parser.add_option("--thumbdrive", dest="thumbdrive", default=THUMBDRIVE, action="store", help="basedir of thumbdrive")
    parser.add_option("--delete-after", dest="deleteafter", default=False, action="store_true", help="add --delete-after to rsync command line (default: %s)")

    (opts, args) = parser.parse_args()

    # sync from falcon to cyclops as "backups"
    # sync from cyclops to falcon as "backups"
    # sync from cyclops to thumbdrive if mounted as "jam"
    # sync ~jam/projects/ to /srv/backups on cyclops as "jam"
    cmds = []
    if opts.mode is None:
        ttyio.echo("specify --mode!", level="error")
        return -1
    elif opts.mode == "cyclops-pgdump-thumbdrive":
        ttyio.echo("syncing *cyclops*.pgdump to thumbdrive")
        cmds.append("/srv/backups/cyclops/pgdumps/*.pgdump %s/backups/cyclops/pgdumps/" % (opts.thumbdrive))
    elif opts.mode == "falcon-pgdump-thumbdrive":
        ttyio.echo("syncing *falcon*.pgdump to thumbdrive")
        cmds.append("/srv/backups/falcon/pgdumps/*.pgdump %s/backups/falcon/pgdumps/" % (opts.thumbdrive))

    elif opts.mode == "thumbdrive":
        if os.path.isdir(opts.thumbdrive) and os.access(opts.thumbdrive, os.W_OK):
             cmds.append("/srv/backups/ %s" % (opts.thumbdrive))
        else:
            ttyio.echo("thumbdrive not mounted or mounted read-only", level="error")
            return -1
    elif opts.mode == "projects":
        # rsync --verbose --recursive --copy-links --exclude .git --exclude .svn ~jam/projects /run/media/jam/6F6A-A171/
        cmds.append("~jam/projects /srv/backups/")
    elif opts.mode == "falcon":
        cmds.append("backups@falcon:/srv/backups/falcon /srv/backups/")
    elif opts.mode == "cyclops":
        cmds.append("/srv/backups/cyclops backups@falcon:/srv/backups/")
    elif opts.mode == "vhosts":
        cmds.append("backups@falcon:/srv/www/vhosts /srv/backups/falcon/")
    elif opts.mode == "home":
        cmds.append("~jam/Pictures /srv/backups/")
        cmds.append("~jam/.ssh/ /srv/backups/ssh/")
    elif opts.mode == "repo":
#        cmds.append("backups@falcon:/srv/repo /srv/backups/falcon/")
        cmds.append("/srv/repo /srv/backups/cyclops/")
    for c in cmds:
        cmd = buildcmd(opts, c)
        res = run(opts, cmd)
        if res < 0:
            return res
    return

if __name__ == "__main__":
    sys.exit(main())
