import logging
from pathlib import Path

import pandas as pd

from dbgbench.framework.grep import GrepBug
from dbgbench.framework.oracles import HangOracle
from dbgbench.resources import get_grep_samples_dir


class Grep5fa8c7c9(GrepBug):
    def __init__(self):
        super().__init__("grep.5fa8c7c9", HangOracle())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    sample_dir = get_grep_samples_dir()

    bug = Grep5fa8c7c9()
    data: pd.DataFrame = bug.execute_samples(sample_dir)
    print(data[["file", "oracle"]])
