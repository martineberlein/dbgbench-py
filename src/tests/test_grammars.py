import unittest

from pathlib import Path
from fandango.language.parse import parse
from fandango.evolution.algorithm import Fandango

class MyTestCase(unittest.TestCase):

    def test_something(self):
        file = open(Path("./resources/grep.fan").resolve())
        grammar, constraints = parse(file)

        print(constraints)

        test_inputs = []
        for _ in range(100):
            inp = grammar.fuzz(max_nodes=100)
            print(inp)
            test_inputs.append(inp)


        tree = grammar.parse("printf 'abcd' | LC_ALL=en_US.UTF-8 timeout 0.5s grep -F ''")
        print(tree)
        print(tree.to_tree())

        # fandango = Fandango(grammar, constraints, initial_population=test_inputs)
        # solutions = fandango.evolve()
        #
        # for solution in solutions:
        #     print(solution)


if __name__ == '__main__':
    unittest.main()
