import random
import os

from typing import Collection

from dbgbench.framework.oraclesresult import OracleResult
from dbgbench.resources import get_grep_grammar_path, get_grep_samples
from dbgbench.framework.util import escape_non_ascii_utf8
from dbgbench.subjects import Grep3c3bdace, Grepc96b0f2c

from fdlearn.interface.fandango import parse
from fdlearn.data.input import FandangoInput
from fdlearn.learner import FandangoLearner
from fdlearn.logger import LoggerLevel
from fdlearn.resources.patterns import Pattern
from fdlearn.refinement.mutation import MutationFuzzer
import hashlib


def stable_hash(value: str, length: int = 8) -> str:
    return hashlib.sha1(value.encode()).hexdigest()[:length]



def generate_more_failing(bug_type_, grammar_, samples_: Collection[FandangoInput]) -> tuple[list[FandangoInput], list[FandangoInput]]:

    def bug_oracle(inp):
        with bug_type_() as bug:
            res = bug.execute_sample(str(inp.tree))
            print(inp, res)
        return res

    seeds = [inp for inp in samples_ if inp.oracle.is_failing()]

    mutation_fuzzer = MutationFuzzer(grammar_, seed_inputs=seeds, oracle=bug_oracle)

    positive_inputs = []
    negative_inputs = []

    while len(positive_inputs) < 100:
        try:
            inp = next(mutation_fuzzer.run(yield_negatives=True))
            if inp.oracle == OracleResult.FAILING:
                positive_inputs.append(inp)
            else:
                negative_inputs.append(inp)
            write_to_file([inp], bug_type_.__name__)
        except StopIteration:
            break

    return positive_inputs, negative_inputs


def write_to_file(inputs: list[FandangoInput], subject_name: str):
    os.makedirs(f"{subject_name}/positive_inputs", exist_ok=True)
    os.makedirs(f"{subject_name}/negative_inputs", exist_ok=True)

    for inp in inputs:
        try:
            filename = f"{subject_name}_{stable_hash(str(inp))}.txt"
            base_dir = subject_name
            directory = "positive_inputs" if inp.oracle.is_failing() else "negative_inputs"
            filepath = os.path.join(base_dir, directory, filename)

            with open(filepath, "w") as f:
                f.write(str(inp))

        except Exception as e:
            print(f"Error writing input: {inp}\nException: {e}")


if __name__ == "__main__":
    random.seed(2)

    from dbgbench.subjects import Grep3c3bdace, Grepc96b0f2c, Grep5fa8c7c9, Grep7aa698d3, Grep3220317a
    bug_type = Grep3220317a

    grep_grammar = get_grep_grammar_path()
    grammar, _ = parse(grep_grammar)

    with bug_type() as bug:
        samples_paths = bug.sample_files()
        samples = [file.read_text() for file in samples_paths]
        result = bug.execute_samples(samples)

    test_inputs = []
    for inp, oracle in result:
        oracle_bool = True if oracle == OracleResult.FAILING else False
        test_inputs.append((escape_non_ascii_utf8(inp), oracle_bool))

    initial_inputs = {
        FandangoInput.from_str(grammar, inp, oracle) for inp, oracle in test_inputs
    }
    for inp in initial_inputs:
        print(inp, inp.oracle)

    pos_inputs, neg_inputs = generate_more_failing(bug_type, grammar, initial_inputs)
    write_to_file(pos_inputs + neg_inputs, bug_type.__name__)
    for inp in pos_inputs:
        print(inp, inp.oracle)

    print(f"Positive inputs: {len(pos_inputs)}")
    print(f"Negative inputs: {len(neg_inputs)}")
    initial_inputs.update(pos_inputs)
    initial_inputs.update(neg_inputs)