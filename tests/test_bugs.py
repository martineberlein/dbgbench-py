import unittest

from fandango.language.parse import Grammar
from fandango.language.tree import DerivationTree

from fdlearn.interface.fandango import parse

from dbgbench.framework.oraclesresult import OracleResult
from dbgbench.resources import get_grep_grammar_path, get_grep_samples, get_find_grammar_path, get_find_samples
from dbgbench.framework.grep import GrepBug
from dbgbench.framework.util import escape_non_ascii_utf8
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

    def test_get_samples_files(self):
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
            self.assertEqual(result, OracleResult.UNDEFINED)