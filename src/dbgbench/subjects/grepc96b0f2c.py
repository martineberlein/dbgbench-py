import pandas as pd

from dbgbench.framework.grep import GrepBug
from dbgbench.framework.oracles import NoNewTextOracle
from dbgbench.resources import get_grep_samples_dir


class Grepc96b0f2c(GrepBug):
    def __init__(self):
        super().__init__("grep.c96b0f2c", NoNewTextOracle())


if __name__ == "__main__":
    sample_dir = get_grep_samples_dir()

    bug = Grepc96b0f2c()
    data: pd.DataFrame = bug.execute_samples(sample_dir)
    print(data[["file", "oracle"]])