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
import logging

from pathlib import Path
from alhazen.helpers import PrefixWriter
from alhazen import external_exec as execute

__input_pattern = re.compile(r"^printf '(.*)' \|")


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


def extract_input(cli):
    match = re.match(__input_pattern, cli)
    if match is None:
        return None
    value = match.group(1)
    script = "printf '{}'\n".format(value)
    try:
        with open("tmpbash.sh", 'w', encoding='utf-8') as tmpbash:
            tmpbash.write(script)
        cmd = ["bash", "tmpbash.sh"]
        output = execute.check_output(cmd, stderr=subprocess.STDOUT, env={"LANG": "C.UTF-8"})
        return output
    except subprocess.CalledProcessError as ex:
        logging.exception("{} for {} (extracted from: {})".format(ex.output, script, cli))
        return None


def execute_sample(identifier, cli):
    subjpath = bug_dir(identifier, "/root/Desktop/") / "grep/src"
    try:
        script = "mkdir alhazen_testdir; " \
                 "pushd alhazen_testdir > /dev/null 2>&1; " \
                 "touch patterns_1.txt patterns_2.txt file.txt test.txt; " \
                 "export PATH={subjpath}:$PATH; " \
                 "{cli};" \
                 "res=$?;" \
                 "printf \"\\n%s terminated\\n\" Grep;" \
                 "popd > /dev/null 2>&1;" \
                 "rm -r alhazen_testdir;" \
                 "exit $res"
        with open("tmpbash.sh", 'w', encoding='utf-8') as tmpbash:
            tmpbash.write(script.format(subjpath=subjpath, cli=cli))
        cmd = ["bash", "tmpbash.sh"]
        output = execute.check_output(cmd, stderr=subprocess.STDOUT)
        return 0, output
    except subprocess.CalledProcessError as ex:
        return ex.returncode, ex.output


def execute_samples(subject, inp_dir):
    outw = PrefixWriter(sys.stdout, "# csv #- ")
    writer = csv.DictWriter(outw,
                            fieldnames=["file", "line", "subject", "output", "oracle", "return code", "input"],
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
                "input": extract_input(cli),
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
