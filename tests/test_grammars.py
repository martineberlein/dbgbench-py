import unittest

from fandango.language.parse import Grammar
from fandango.language.tree import DerivationTree

from fdlearn.interface.fandango import parse

from dbgbench.resources import get_grep_grammar_path, get_grep_samples, get_find_grammar_path, get_find_samples
from dbgbench.framework.util import escape_non_ascii_utf8


class GrammarTest(unittest.TestCase):
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

    def test_grep_grammar_is_grammar_instance(self):
        self.assertIsInstance(self.grep_grammar, Grammar)
    
    def test_find_grammar_is_grammar_instance(self):
        self.assertIsInstance(self.find_grammar, Grammar)

    def test_grep_grammar_fuzz_generation(self):
        trees = [self.grep_grammar.fuzz(max_nodes=100) for _ in range(100)]
        self.assertTrue(all(isinstance(t, DerivationTree) for t in trees))
    
    def test_find_grammar_fuzz_generation(self):
        trees = [self.find_grammar.fuzz(max_nodes=100) for _ in range(100)]
        self.assertTrue(all(isinstance(t, DerivationTree) for t in trees))

    def test_parsing_grep_initial_samples(self):
        for sample in self.grep_samples:
            with self.subTest(sample=sample):
                escaped = escape_non_ascii_utf8(sample)
                parsed = self.grep_grammar.parse(escaped)
                self.assertIsInstance(
                    parsed, DerivationTree, f"Failed for {sample}"
                    )
    
    def test_parsing_find_initial_samples(self):
        for sample in self.find_samples:
            with self.subTest(sample=sample):
                #escaped = escape_non_ascii_utf8(sample)
                parsed = self.find_grammar.parse(sample)
                #self.assertIsInstance(
                #    parsed, DerivationTree, f"Failed for {sample}"
                #    )
                

if __name__ == "__main__":
    unittest.main()
