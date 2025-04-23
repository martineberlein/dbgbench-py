from dbgbench.framework.genson import GensonBug
from dbgbench.framework.oracles import NullPointerException
from dbgbench.resources import get_genson_samples


class Genson120(GensonBug):
    def __init__(self):
        super().__init__("genson.120", NullPointerException())
        self._jar = "./genson/genson_subject.jar"


if __name__ == "__main__":
    samples = get_genson_samples()

    with Genson120() as bug:
        result = bug.execute_samples(samples)
       

    for inp, oracle in result:
        print(inp.ljust(80), oracle, "\n")
