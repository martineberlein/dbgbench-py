from dbgbench.framework.grep import GrepBug
from dbgbench.framework.oracles import SegvOracle
from dbgbench.resources import get_grep_samples


class Grep3220317a(GrepBug):
    def __init__(self):
        super().__init__("grep.3220317a", SegvOracle())


if __name__ == "__main__":
    samples = get_grep_samples()

    with Grep3220317a() as bug:
        result = bug.execute_samples(bug.sample_inputs())

    for inp, oracle in result:
        print(inp.ljust(80), oracle)
