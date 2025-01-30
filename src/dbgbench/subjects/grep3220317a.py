import pandas as pd

from dbgbench.framework.grep import GrepBug
from dbgbench.framework.oracles import SegvOracle
from dbgbench.resources import get_grep_samples_dir


class Grep3220317a(GrepBug):
    def __init__(self):
        super().__init__("grep.3220317a", SegvOracle())


if __name__ == "__main__":
    sample_dir = get_grep_samples_dir()

    bug = Grep3220317a()
    data: pd.DataFrame = bug.execute_samples(sample_dir)
    print(data[["file", "oracle"]])