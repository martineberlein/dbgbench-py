from dbgbench.framework.find import FindBug
from dbgbench.framework.oracles import HangOracle
from dbgbench.resources import get_find_samples


class Findff248a20(FindBug):
    def __init__(self):
        super().__init__("find.ff248a20", HangOracle())


if __name__ == "__main__":
    samples = get_find_samples()

    with Findff248a20() as bug:
        result = bug.execute_samples(samples)

    for inp, oracle in result:
        print(inp.ljust(80), oracle)