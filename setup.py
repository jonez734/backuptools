#!/usr/bin/env python
from setuptools import setup
import time

v = time.strftime("%Y%m%d%H%M")
projectname = "backups"

setup(
  name=projectname,
  description="a set of Python scripts to make backups",
  version=v,
  url="http://projects.zoidtechnologies.com/%s/" % (projectname),
  author="zoidtechnologies.com",
  author_email="%s@projects.zoidtechnologies.com" % (projectname),
  scripts=["backupdatabase", "syncbackups"],
  py_modules=["backupdatabase", "syncbackups"],
  requires=["bbsengine6"],
  license="GPLv2"
)
