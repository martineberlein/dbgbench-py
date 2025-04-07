import unittest

from fandango.language.parse import Grammar
from fandango.language.tree import DerivationTree

from fdlearn.interface.fandango import parse

from dbgbench.framework.oraclesresult import OracleResult
from dbgbench.resources import get_grep_grammar_path, get_grep_samples, get_find_grammar_path, get_find_samples
from dbgbench.framework.util import escape_non_ascii_utf8
from dbgbench.subjects import *

class OracleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        #grep
        grep_grammar_path = get_grep_grammar_path()
        cls.grep_grammar, cls.grep_constraints = parse(grep_grammar_path)
        cls.grep_samples = get_grep_samples()

        #find
        find_grammar_path = get_find_grammar_path()
        cls.find_grammar, cls.find_constraints = parse(find_grammar_path)
        cls.find_samples = get_find_samples()


    def test_grep_oracle(self):
        test_inputs = {
            "printf 'haha\\n' | LC_ALL=tr_TR.utf8 timeout 0.5s grep -i 'ha'": OracleResult.PASSING,
            "printf 'X' | timeout 0.5s grep -E -q '(^| )*( |$)'": OracleResult.FAILING,
        }

        with Grep3c3bdace() as bug:
            results = bug.execute_samples(list(test_inputs.keys()))

        self.assertEqual(len(results), 2)
        for inp, oracle in results:
            self.assertEqual(test_inputs[inp], oracle)

    def test_grep_grammar_fuzzer_oracle(self):
        trees = [str(self.grep_grammar.fuzz(max_nodes=100)) for _ in range(100)]

        with Grep3c3bdace() as bug:
            results = bug.execute_samples(trees)
        for inp, oracle in results:
            print(oracle, inp, "\n")

if __name__ == "__main__":
    unittest.main()