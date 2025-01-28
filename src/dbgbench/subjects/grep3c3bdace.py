# docker
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
    import sys
    print(Path("../resources/samples/").resolve())
    with create_bug() as bug:
        data: pandas.DataFrame = bug.execute_samples(Path("../resources/samples/").resolve())
        print(data[["file", "oracle", "output", "oracle"]])
        # for row in data.iterrows():
        #     print(row)
        #     print(bug.apply_oracle_single(row))

