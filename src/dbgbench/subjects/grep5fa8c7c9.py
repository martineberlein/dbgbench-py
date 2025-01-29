import logging
from pathlib import Path

import pandas as pd

from dbgbench.framework.grep import GrepBug
from dbgbench.framework.oracles import HangOracle


def create_bug():
    return GrepBug("grep.5fa8c7c9", HangOracle())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with create_bug() as bug:
        samples_dir = Path("../resources/samples/").resolve()
        data: pd.DataFrame = bug.execute_samples(samples_dir)
        print(data[["file", "oracle"]])
        print(data[["file", "output"]])
