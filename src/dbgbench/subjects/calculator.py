from dbgbench.framework.genson import GensonBug
from dbgbench.framework.oracles import NullPointerException
from dbgbench.resources import get_calculator_samples, get_ubuntu_dockerfile
from dbgbench.framework.python_bug import PythonBug
from pathlib import Path

class CalculatorBug(PythonBug):
    def __init__(self):
        super().__init__("calc")
        self._faulty_py = Path("src/dbgbench/resources/python_files/calculator/main.py").resolve()
        
    def _get_dockerfile_dir(self):
        return get_ubuntu_dockerfile()
    
    def _setup_container_files(self):
        self.container().copy_into([self._faulty_py], "/root/Desktop/scripts")

    def sample_files(self):
        return get_calculator_samples()
    
    def grammar_file(self):
        pass

if __name__ == "__main__":
    samples = get_calculator_samples()

    with CalculatorBug() as bug:
        result = bug.execute_samples(samples)
       

    for inp, oracle in result:
        print(inp.ljust(80), oracle, "\n")