#!/usr/bin/env python
from setuptools import setup
import time

v = time.strftime("%Y%m%d%H%M")
projectname = "backuptools"

setup(
    name=projectname,
    description="a set of Python scripts to make backups",
    version=v,
    url=f"http://projects.zoidtechnologies.com/{projectname}/",
    author="zoidtechnologies.com",
    author_email=f"{projectname}@projects.zoidtechnologies.com",
    scripts=["backupdatabase", "syncbackups"],
    py_modules=["backupdatabase", "syncbackups"],
    requires=["bbsengine6"],
    license="GPLv2",
)
