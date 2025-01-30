import unittest
import random

from pathlib import Path
from fandango.language.parse import parse, Grammar
from fandango.language.tree import DerivationTree

from dbgbench.framework.oraclesresult import OracleResult
from dbgbench.subjects.grep3c3bdace import create_bug


class GrepBugsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        random.seed(1)

        grammar_path = Path("./resources/grep.fan").resolve()
        with grammar_path.open() as f:
            cls.grammar, cls.constraints = parse(f)

    @staticmethod
    def escape_non_ascii_utf8(s):
        escaped = []
        for ch in s:
            if ord(ch) < 128:
                escaped.append(ch)
            else:
                for b in ch.encode("utf-8"):
                    escaped.append("\\x{:02X}".format(b))
        return "".join(escaped)

    @staticmethod
    def unescape_hex_utf8(s):
        # Parse the string and reconstruct bytes from both plain ASCII
        # and \xHH sequences, then decode once as UTF-8.
        i = 0
        out_bytes = []
        while i < len(s):
            # Look for a pattern like \xAB
            if (s[i] == '\\'
                    and i + 3 < len(s)
                    and s[i + 1] == 'x'
                    and all(c in '0123456789ABCDEFabcdef' for c in s[i + 2:i + 4])):
                hex_part = s[i + 2:i + 4]
                out_bytes.append(int(hex_part, 16))
                i += 4
            else:
                out_bytes.append(ord(s[i]))
                i += 1
        return bytes(out_bytes).decode('utf-8', errors='replace')

    def test_grammar_is_grammar_instance(self):
        self.assertIsInstance(self.grammar, Grammar)

    def test_grammar_fuzz_generation(self):
        trees = [self.grammar.fuzz(max_nodes=100) for _ in range(100)]
        self.assertTrue(all(isinstance(t, DerivationTree) for t in trees))

    def test_parsing_initial_samples(self):
        sample_dir = Path("../dbgbench/resources/samples")
        for sample_file in sample_dir.iterdir():
            if sample_file.is_file():
                with self.subTest(sample_file=sample_file):
                    with sample_file.open(encoding="utf-8") as f:
                        inp = self.escape_non_ascii_utf8(f.read())
                        parsed = self.grammar.parse(inp)
                    self.assertIsInstance(
                        parsed, DerivationTree, f"Failed for {sample_file}"
                    )

    def test_oracle(self):
        test_inputs = {
            "printf 'haha\\n' | LC_ALL=tr_TR.utf8 timeout 0.5s grep -i 'ha'": OracleResult.NO_BUG,
            "printf 'X' | timeout 0.5s grep -E -q '(^| )*( |$)'": OracleResult.BUG,
        }

        with create_bug() as bug:
            results = bug.execute_samples_with_oracle(test_inputs.keys())
            for inp, oracle in results:
                self.assertEqual(test_inputs[inp], oracle)

    def test_grammar_fuzzer_oracle(self):
        trees = [str(self.grammar.fuzz(max_nodes=100)) for _ in range(100)]

        with create_bug() as bug:
            results = bug.execute_samples_with_oracle(trees)
            for inp, oracle in results:
                print(oracle, inp)


if __name__ == "__main__":
    unittest.main()
