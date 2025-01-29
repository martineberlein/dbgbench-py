from pathlib import Path
import subprocess
import bz2
from shutil import copyfileobj

"""
There is a problem with subprocess.run(): It uses fork(), which allocates as much memory as the parent process has. 
This quickly leads to out-of-memory situations. 

In order to prevent this, external_execute forks from within a parallel process. If setup() was not called, 
it falls back to just using subprocess.
"""

pool = None


def make_cmd(cmd):
    def clean(c):
        if isinstance(c, Path):
            return str(c.resolve())
        else:
            return c
    return [clean(c) for c in cmd]


def synchronous_run(cmd, logfile, kwargs):
    if logfile is not None:
        lfp = Path(logfile)
        if lfp.exists():
            mode = 'ab'
        else:
            mode = 'wb'
        with bz2.open(logfile, mode) as log:
            log.write(" ".join(cmd).encode(encoding="UTF-8"))
            log.write("\n".encode(encoding="UTF-8"))
            log.flush()
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
                copyfileobj(process.stdout, log)
                retcode = process.wait()
                if 0 != retcode:
                    raise subprocess.CalledProcessError(retcode, process.args)
                return subprocess.CompletedProcess(process.args, retcode)
    else:
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)


def synchronous_check_output(cmd, kwargs):
    return subprocess.check_output(cmd, **kwargs)


def run(cmd, logfile, **kwargs):
    cmd = make_cmd(cmd)
    return synchronous_run(cmd, logfile, kwargs)


def check_output(cmd, **kwargs):
    cmd = make_cmd(cmd)
    return synchronous_check_output(cmd, kwargs)
