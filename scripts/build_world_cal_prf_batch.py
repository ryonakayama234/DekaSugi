#!/usr/bin/env python3
"""Explicit optional accelerator build. No runtime build/import side effects."""
import os
import pathlib
import shlex
import subprocess
import sysconfig

ROOT=pathlib.Path(__file__).resolve().parents[1]

def build():
    source=ROOT/'world_cal/prf_batch.c'
    target=ROOT/('world_cal/_prf_batch'+sysconfig.get_config_var('EXT_SUFFIX'))
    command=shlex.split(os.environ.get('CC','cc'))+[
        '-shared','-fPIC','-O2','-fno-fast-math','-ffp-contract=off',
        '-Wno-deprecated-declarations','-I'+sysconfig.get_path('include'),
        str(source),'-o',str(target),'-lcrypto','-lm']
    subprocess.run(command,check=True)
    print(target)

if __name__=='__main__':build()
