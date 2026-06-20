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
    scripts=["syncbackups"],
    py_modules=["syncbackups"],
    requires=["bbsengine6"],
    license="GPLv2",
)
