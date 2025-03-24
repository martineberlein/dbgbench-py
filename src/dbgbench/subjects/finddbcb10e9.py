from dbgbench.framework.find import FindBug
from dbgbench.framework.oracles import SegvOracle
from dbgbench.resources import get_find_samples


class Finddbcb10e9(FindBug):
    def __init__(self):
        super().__init__("find.dbcb10e9", SegvOracle())


if __name__ == "__main__":
    samples = get_find_samples()

    with Finddbcb10e9() as bug:
        result = bug.execute_samples(samples)

    for inp, oracle in result:
        print(inp.ljust(80), oracle)