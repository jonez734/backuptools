#!/usr/bin/env python

import os
from optparse import OptionParser

def main():
    parser = OptionParser(usage="usage: %prog [options] projectid")
    parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_option("--debug", default=True, action="store_true", help="run %prog in debug mode")
    parser.add_option("--mode", default=None, action="store", help="specify mode for backups sync (thumbdrive, projects, or falcon)")

    (opts, args) = parser.parse_args()

    # sync from falcon to cyclops
    # sync from cyclops to falcon
    # sync from cyclops to thumbdrive if mounted as "jam"
    # sync ~jam/projects/ to /srv/backups on cyclops as "jam"
    if opts.mode == "thumbdrive":
        THUMBDRIVE = "/run/media/jam/6F6A-A171"
        if os.path.isdir(THUMBDRIVE) and os.access(THUMBDRIVE, os.W_OK):
            os.system("rsync --recursive --verbose --human-readable /srv/backups /run/media/jam/6F6A-A171/")
    elif opts.mode == "falcon":
        os.system("rsync --verbose --recursive --human-readable backups@falcon:/srv/backups/ /srv/backups/")
        os.system("rsync --verbose --recursive --human-readable /srv/backups/ backups@falcon:/srv/backups/")
    elif opts.mode == "projects":
        os.system("rsync --verbose --recursive --exclude='.sass-cache' ~jam/projects /srv/backups/")

if __name__ == "__main__":
    main()
