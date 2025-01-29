import logging
from pathlib import Path

import pandas

from dbgbench.framework import grep, oracles

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s:%(levelname)s: %(message)s",
)

def create_bug():
    return grep.GrepBug("grep.3c3bdace", oracles.SegvOracle())


if __name__ == "__main__":
    with create_bug() as bug:
        data: pandas.DataFrame = bug.execute_samples(Path("../resources/samples/").resolve())
        print(data[["file", "oracle"]])
