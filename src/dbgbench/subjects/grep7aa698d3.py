# docker
import logging
from pathlib import Path

import pandas

from dbgbench.framework import grep, oracles


def create_bug():
    return grep.GrepBug("grep.7aa698d3", oracles.NoNewLineOracle())


if __name__ == "__main__":
    with create_bug() as bug:
        data: pandas.DataFrame = bug.execute_samples(Path("../resources/samples/").resolve())
        print(data[["file", "oracle"]])