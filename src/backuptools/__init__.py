#!/usr/bin/env python3
from . import lib


def init(args, **kwargs) -> bool:
    return True


def access(args, op, **kwargs) -> bool:
    return True


def buildargs(args, **kwargs):
    return None


def main(args, **kwargs):
    return lib.runmodule(args, "main", **kwargs)
