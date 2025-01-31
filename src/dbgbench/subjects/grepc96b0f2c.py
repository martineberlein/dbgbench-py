from dbgbench.framework.grep import GrepBug
from dbgbench.framework.oracles import NoNewTextOracle
from dbgbench.resources import get_grep_samples


class Grepc96b0f2c(GrepBug):
    def __init__(self):
        super().__init__("grep.c96b0f2c", NoNewTextOracle())


if __name__ == "__main__":
    samples = get_grep_samples()

    with Grepc96b0f2c() as bug:
        result = bug.execute_samples(samples)

    for inp, oracle in result:
        print(inp.ljust(80), oracle)
