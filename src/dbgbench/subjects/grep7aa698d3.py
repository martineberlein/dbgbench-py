import pandas as pd

from dbgbench.framework.grep import GrepBug
from dbgbench.framework.oracles import NoNewLineOracle
from dbgbench.resources import get_grep_samples_dir


class Grep7aa698d3(GrepBug):
    def __init__(self):
        super().__init__("grep.7aa698d3", NoNewLineOracle())


if __name__ == "__main__":
    sample_dir = get_grep_samples_dir()

    bug = Grep7aa698d3()
    data: pd.DataFrame = bug.execute_samples(sample_dir)
    print(data[["file", "oracle"]])
