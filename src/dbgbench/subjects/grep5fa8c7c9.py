from dbgbench.framework.grep import GrepBug
from dbgbench.framework.oracles import HangOracle
from dbgbench.resources import get_grep_samples


class Grep5fa8c7c9(GrepBug):
    def __init__(self):
        super().__init__("grep.5fa8c7c9", HangOracle())


if __name__ == "__main__":
    samples = get_grep_samples()

    with Grep5fa8c7c9() as bug:
        result = bug.execute_samples(samples)

    for inp, oracle in result:
        print(inp.ljust(80), oracle)
