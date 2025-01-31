from dbgbench.framework.grep import GrepBug
from dbgbench.framework.oracles import SegvOracle
from dbgbench.resources import get_grep_samples


class Grep3c3bdace(GrepBug):
    def __init__(self):
        super().__init__("grep.3c3bdace", SegvOracle())


if __name__ == "__main__":
    samples = get_grep_samples()

    with Grep3c3bdace() as bug:
        result = bug.execute_samples(samples)

    for inp, oracle in result:
        print(inp.ljust(80), oracle)
