from dbgbench.framework.grep import GrepBug
from dbgbench.framework.oracles import NoNewLineOracle
from dbgbench.resources import get_grep_samples


class Grep7aa698d3(GrepBug):
    def __init__(self):
        super().__init__("grep.7aa698d3", NoNewLineOracle())


if __name__ == "__main__":
    samples = get_grep_samples()

    with Grep7aa698d3() as bug:
        result = bug.execute_samples(samples)

    for inp, oracle in result:
        print(inp.ljust(80), oracle)
