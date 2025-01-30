import logging
from pathlib import Path

import pandas as pd

from dbgbench.framework.grep import GrepBug
from dbgbench.framework.oracles import SegvOracle
from dbgbench.resources import get_grep_samples_dir


logging.basicConfig(
    level=logging.INFO,
    format="%(name)s:%(levelname)s: %(message)s",
)

class Grep3c3bdace(GrepBug):
    def __init__(self):
        super().__init__("grep.3c3bdace", SegvOracle())


if __name__ == "__main__":
    sample_dir = get_grep_samples_dir()

    bug = Grep3c3bdace()
    data: pd.DataFrame = bug.execute_samples(sample_dir)
    print(data[["file", "oracle"]])
