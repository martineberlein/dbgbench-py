import unittest

from fandango.language.parse import Grammar
from fandango.language.tree import DerivationTree

from fandangoLearner.interface.fandango import parse

from dbgbench.framework.oraclesresult import OracleResult
from dbgbench.resources import get_grep_grammar_path, get_grep_samples
from dbgbench.framework.util import escape_non_ascii_utf8
from dbgbench.subjects import *


class GrepBugsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        grammar_path = get_grep_grammar_path()
        cls.grammar, cls.constraints = parse(grammar_path)

        cls.samples = get_grep_samples()

    def test_grammar_is_grammar_instance(self):
        self.assertIsInstance(self.grammar, Grammar)

    def test_grammar_fuzz_generation(self):
        trees = [self.grammar.fuzz(max_nodes=100) for _ in range(100)]
        self.assertTrue(all(isinstance(t, DerivationTree) for t in trees))

    def test_parsing_initial_samples(self):
        for sample in self.samples:
            with self.subTest(sample=sample):
                escaped = escape_non_ascii_utf8(sample)
                parsed = self.grammar.parse(escaped)
                self.assertIsInstance(
                    parsed, DerivationTree, f"Failed for {sample}"
                    )

    def test_oracle(self):
        test_inputs = {
            "printf 'haha\\n' | LC_ALL=tr_TR.utf8 timeout 0.5s grep -i 'ha'": OracleResult.PASSING,
            "printf 'X' | timeout 0.5s grep -E -q '(^| )*( |$)'": OracleResult.FAILING,
        }

        with Grep3c3bdace() as bug:
            results = bug.execute_samples(list(test_inputs.keys()))

        self.assertEqual(len(results), 2)
        for inp, oracle in results:
            self.assertEqual(test_inputs[inp], oracle)

    def test_grammar_fuzzer_oracle(self):
        trees = [str(self.grammar.fuzz(max_nodes=100)) for _ in range(100)]

        with Grep3c3bdace() as bug:
            results = bug.execute_samples(trees)
        for inp, oracle in results:
            print(oracle, inp)

    def test_grep_bugs(self):
        bugs = [
            Grep3c3bdace,
            Grep5fa8c7c9,
            Grep7aa698d3,
            Grep3220317a,
            Grepc96b0f2c
        ]
        for bug_type in bugs:
            with self.subTest(bug_type=bug_type):
                with bug_type() as bug:
                    result = bug.execute_samples(self.samples)
                self.assertEqual(len(result), 11)
                self.assertFalse(all(oracle == OracleResult.PASSING for _, oracle in result))
                self.assertTrue(any(oracle == OracleResult.FAILING for _, oracle in result))
                self.assertTrue(all(isinstance(inp, str) for inp, _ in result))

    def test_get_samples_files(self):
        bugs = [
            #Grep3c3bdace,
            # Grep5fa8c7c9,
            # Grep7aa698d3,
            # Grep3220317a,
            Grepc96b0f2c
        ]
        for bug_type in bugs:
            with self.subTest(bug_type=bug_type):
                with bug_type() as bug:
                    sample_inputs = bug.sample_inputs()
                    print(sample_inputs)
                    result = bug.execute_samples(sample_inputs)
                    print(result)
                    self.assertEqual(len(result),2)
                    self.assertTrue(any([oracle.is_failing() for _, oracle in result]))
                    self.assertTrue(any([not oracle.is_failing() for _, oracle in result]))

    def test_c9_special_inputs(self):
        inps = ["""printf '\\x50\\x00\\n\\n\\nb' | GREP_COLOR='00;02;2;0;02;00;00;2;00;0' timeout 0.5s grep -i -n ''""",
                """printf 'a\\n\\na' | LC_ALL=en_US.utf8 timeout 0.5s grep -i -n '^$'"""]
        with Grepc96b0f2c() as bug:
            result = bug.execute_samples(inps)
            print(result)
            #self.assertEqual(result, OracleResult.UNDEFINED)

if __name__ == "__main__":
    unittest.main()
