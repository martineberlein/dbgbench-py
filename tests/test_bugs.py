import unittest

from fdlearn.interface.fandango import parse

from dbgbench.framework.oraclesresult import OracleResult
from dbgbench.resources import get_grep_grammar_path, get_grep_samples, get_find_grammar_path, get_find_samples
from dbgbench.framework.grep import GrepBug
from dbgbench.framework.find import FindBug
from dbgbench.subjects import *


class BugsTest(unittest.TestCase):
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

    def test_find_get_samples_files(self):
        bugs = [
            Find07b941b1,
            Find091557f6,
            Finddbcb10e9,
            Findff248a20
        ]

        for bug_type in bugs:
            with self.subTest(bug_type=bug_type):
                with bug_type() as bug:
                    bug : FindBug
                    sample_inputs = bug.sample_inputs()
                    result = bug.execute_samples(sample_inputs)
                    print(result, "\n")
                    self.assertEqual(len(result),2)
                    self.assertTrue(any([oracle.is_failing() for _, oracle in result]))
                    self.assertTrue(any([not oracle.is_failing() for _, oracle in result]))

    def test_grep_get_samples_files(self):
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
                    bug : GrepBug
                    sample_inputs = bug.sample_inputs()
                    result = bug.execute_samples(sample_inputs)
                    print(bug._bug_id, result, "\n")
                    self.assertEqual(len(result),2)
                    self.assertTrue(any([oracle == OracleResult.FAILING for _, oracle in result]))
                    self.assertTrue(any([oracle == OracleResult.PASSING for _, oracle in result]))

    def test_find_bugs(self):
        bugs = [
            Find07b941b1,
            Find091557f6,
            Finddbcb10e9,
            Findff248a20
        ]
        for bug_type in bugs:
            with self.subTest(bug_type=bug_type):
                with bug_type() as bug:
                    bug: FindBug
                    result = bug.execute_samples(self.find_samples)
                print(result, "\n")
                self.assertEqual(len(result), 11)
                self.assertFalse(all(oracle == OracleResult.PASSING for _, oracle in result))
                self.assertTrue(any(oracle == OracleResult.FAILING for _, oracle in result))
                self.assertTrue(all(isinstance(inp, str) for inp, _ in result))

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
                    bug: GrepBug
                    result = bug.execute_samples(self.grep_samples)
                
                self.assertEqual(len(result), 11)
                self.assertFalse(all(oracle == OracleResult.PASSING for _, oracle in result))
                self.assertTrue(any(oracle == OracleResult.FAILING for _, oracle in result))
                self.assertTrue(all(isinstance(inp, str) for inp, _ in result))

    def test_grep_c9_special_inputs(self):
        inps = ["""printf '\\x50\\x00\\n\\n\\nb' | GREP_COLOR='00;02;2;0;02;00;00;2;00;0' timeout 0.5s grep -i -n ''""",
                """printf 'a\\n\\na' | LC_ALL=en_US.utf8 timeout 0.5s grep -i -n '^$'"""]
        with Grepc96b0f2c() as bug:
            result = bug.execute_samples(inps)
            print(result)
            self.assertEqual(result, OracleResult.UNDEFINED)

if __name__ == "__main__":
    unittest.main()