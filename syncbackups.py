#!/usr/bin/env python

import os, sys
from optparse import OptionParser
import bbsengine4 as bbsengine

def buildbuf(opts):
    buf = []
    buf.append("rsync")
    buf.append("--recursive")
    buf.append("--human-readable")
    buf.append("--chmod=Dg=rwxs,Fgu=rw,Fo=r")
    buf.append("--group")
    buf.append("--update --backup")
    buf.append("--rsh=ssh --delete-after --links")
    buf.append("--exclude '.~lock*' --exclude '*~' --exclude '443'")

    if opts.verbose is True:
        buf.append("--verbose")
    if opts.dryrun is True:
        buf.append("--dry-run")
    if sys.stdout.isatty() is True:
        buf.append("--progress")
    return buf

THUMBDRIVE = "/run/media/jam/6F6A-A171"

def run(buf):
    b = " ".join(buf)
    print b
    res = os.system(b)
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

    (opts, args) = parser.parse_args()

    # sync from falcon to cyclops as "backups"
    # sync from cyclops to falcon as "backups"
    # sync from cyclops to thumbdrive if mounted as "jam"
    # sync ~jam/projects/ to /srv/backups on cyclops as "jam"
    buf = buildbuf(opts)
    if opts.mode is None:
        print "specify --mode!"
        return -1
    elif opts.mode == "thumbdrive":
        if os.path.isdir(opts.thumbdrive) and os.access(opts.thumbdrive, os.W_OK):
             buf.append("/srv/backups/ %s" % (opts.thumbdrive))
        else:
            print "thumbdrive not mounted"
            return -1
    elif opts.mode == "projects":
        buf.append("~jam/projects /srv/backups/")
    elif opts.mode == "falcon":
        buf.append("backups@falcon:/srv/backups/falcon /srv/backups/")
    elif opts.mode == "cyclops":
        buf.append("/srv/backups/cyclops backups@falcon:/srv/backups/")
    elif opts.mode == "vhosts":
        buf.append("backups@falcon:/srv/www/vhosts /srv/backups/falcon/")
    res = run(buf)
    return res

if __name__ == "__main__":
    sys.exit(main())
