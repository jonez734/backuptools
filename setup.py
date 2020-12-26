#!/usr/bin/env python
from distutils.core import setup

import time

v = time.strftime("%Y%m%d%H%M")
projectname = "backups"

setup(
  name=projectname,
  description="a set of Python scripts to make backups",
  version=v,
  url="http://projects.zoidtechnologies.com/%s/" % (projectname),
  author="zoid technologies",
  author_email="%s@projects.zoidtechnologies.com" % (projectname),
  scripts=["backupdatabase", "syncbackups"],
  py_modules=["backupdatabase", "syncbackups"],
  requires=["ttyio4"],
  license="GPLv2"
)
