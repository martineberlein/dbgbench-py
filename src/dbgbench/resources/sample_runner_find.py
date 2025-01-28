#!/bin/env python3

"""
This script runs all samples in the given directory, and
writes a csv with all the data to stdout.

It needs to be able to execute within the dbgbench python container,
which has an outdated python version, so some newer syntax may not be available.
"""
import re
import sys
import shutil
import codecs
import csv
import subprocess
import os

from pathlib import Path
from alhazen.helpers import PrefixWriter
from alhazen import external_exec as execute

__input_pattern = re.compile(r"^printf '(.*)' \|")


def shell_functions():
    return """mkcd () {
                mkdir $1 &>/dev/null && pushd $1 &>/dev/null
              }
              al_popd () {
                popd &>/dev/null
              }
              al_ln () {
                ln $@ &>/dev/null
              }
              al_touch () {
                touch $@ &>/dev/null
              }"""


def build_chroot(subject):
    # prepare directory
    dir = Path("/tmp/test_alhazen/")
    bin_dir = dir / "bin"
    if not bin_dir.exists():
        bin_dir.mkdir(parents=True)
    # copy the subject
    if subject is not None:
        shutil.copy(str(subject.resolve()), str((bin_dir / "find").resolve()))
    # copy required helper programs
    for prog in ["bash", "touch", "ls", "mkdir", "rm", "ln", "timeout"]:
        progfile = Path("/bin") / prog
        if not progfile.exists():
            progfile = Path("/usr/bin") / prog
        targetfile = bin_dir / prog
        shutil.copy(str(progfile.resolve()), str(targetfile.resolve()))

    # write a script which sets up everything as required for a chroot
    script = "#!/bin/bash\n" \
             "CHROOT={testdir}\n" \
             "for PROG in $(find $CHROOT/bin -executable); do\n" \
             "ldd $PROG | egrep -o '/lib.*\.[0-9]' | xargs -n 1 -I{{}} cp --parents {{}} $CHROOT\n" \
             "done\n" \
             "mkdir $CHROOT/dev/\n" \
             "mknod -m 666 $CHROOT/dev/null c 1 3\n" \
             "mknod -m 666 $CHROOT/dev/zero c 1 5\n"
    with open(str((dir / "ldd_script.sh").resolve()), 'w', encoding='utf-8') as tmpbash:
        tmpbash.write(script.format(testdir=dir.resolve()))
    # and execute the script
    cmd = ["bash", str((dir / "ldd_script.sh").resolve())]
    execute.check_output(cmd, cwd=str(dir.resolve()), stderr=subprocess.STDOUT)
    # return the dir
    return dir


def bug_dir(identifier, basedir):
    basedir = Path(basedir)
    i = 1
    subject = identifier[:identifier.rfind(".")]
    while True:
        check = basedir / "{subj}{i}".format(subj=subject, i=i)
        if check.exists():
            id_file = check / identifier
            if id_file.exists():
                return check
        else:
            raise AssertionError("I could not find {subj} for {iden} (round: {i}, looking in {basedir})".format(
                subj=subject,
                iden=identifier,
                i=i,
                basedir=basedir))
        i = i + 1


def execute_sample(identifier, cli):
    subjdir = bug_dir(identifier, "/root/Desktop/") / "find" / "find"
    chroot_dir = build_chroot(subjdir / "find")
    try:
        env = os.environ.copy()
        env['LANG'] = "C.UTF-8"
        script = "#!/bin/bash\n" \
                 "{funcs}\n" \
                 "{cli}\n" \
                 "res=$?\n" \
                 "exit $res\n\n"
        with open(str((chroot_dir / "tmpbash.sh").resolve()), 'w', encoding='utf-8') as tmpbash:
            tmpbash.write(script.format(cli=cli, funcs=shell_functions()))
        cmd = ["chroot", str(chroot_dir.resolve()), '/bin/bash', "/tmpbash.sh"]
        output = execute.check_output(cmd, cwd=str(chroot_dir.resolve()), stderr=subprocess.STDOUT, env=env)
        return 0, output
    except subprocess.CalledProcessError as ex:
        return ex.returncode, ex.output
    finally:
        # tidy up the chroot
        shutil.rmtree(str(chroot_dir.resolve()))


def execute_samples(subject, inp_dir):
    outw = PrefixWriter(sys.stdout, "# csv #- ")
    writer = csv.DictWriter(outw,
                            fieldnames=["file", "line", "subject", "output", "oracle", "return code"],
                            dialect='unix')
    writer.writeheader()
    for config_file in inp_dir.iterdir():
        if str(config_file).endswith(".cli"):
            with open(config_file, 'r') as inf:
                cli = inf.read()
            rc, output = execute_sample(subject, cli)

            if len(output) > 5000:
                output = output[0:5000]
            entry = {
                "file": str(config_file.name),
                "line": cli,
                "subject": subject,
                "output": output,
                "return code": rc
            }
            writer.writerow(entry)
            outw.flush()


if __name__ == "__main__":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    if 3 != len(sys.argv) and 4 != len(sys.argv):
        print("Usage:", sys.argv[0], "<identifier>", "<working_dir> [rm]")
        exit(1)
    execute_samples(sys.argv[1], Path(sys.argv[2]))
    if 4 == len(sys.argv) and 'rm' == sys.argv[3]:
        shutil.rmtree(sys.argv[2])
