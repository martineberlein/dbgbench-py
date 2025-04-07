from dbgbench.framework.find import FindBug
from dbgbench.framework.oracles import OutputSubstringOracle
from dbgbench.resources import get_find_samples


class Find091557f6(FindBug):
    def __init__(self):
        super().__init__("find.091557f6", OutputSubstringOracle(b'pred.c:1578:'))


if __name__ == "__main__":
    samples = get_find_samples()

    with Find091557f6() as bug:
        result = bug.execute_samples(samples)

    for inp, oracle in result:
        print(inp.ljust(80), oracle, "\n")