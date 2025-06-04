import random
import os

from typing import Collection

from dbgbench.framework.oraclesresult import OracleResult
from dbgbench.resources import get_genson_grammar_path
from dbgbench.framework.util import escape_non_ascii_utf8
from dbgbench.framework.genson import GensonBug
from dbgbench.framework.java_bug import JavaBug

from fdlearn.interface.fandango import parse
from fdlearn.data.input import FandangoInput
from fdlearn.refinement.mutation import MutationFuzzer
import hashlib


def stable_hash(value: str, length: int = 8) -> str:
    return hashlib.sha1(value.encode()).hexdigest()[:length]



def generate_more_failing(bug_type_, grammar_, samples_: Collection[FandangoInput]) -> tuple[list[FandangoInput], list[FandangoInput]]:

    def bug_oracle(inp: FandangoInput):
        with bug_type_() as bug:
            bug: GensonBug
            res = bug.execute_sample(str(inp.tree))
            print(inp, res)
        return res

    seeds = [inp for inp in samples_ if inp.oracle.is_failing()]

    mutation_fuzzer = MutationFuzzer(grammar_, seed_inputs=seeds, oracle=bug_oracle)

    positive_inputs = set()
    negative_inputs = set()

    while len(positive_inputs) < 100 or len(negative_inputs) < 100:
        try:
            inp = next(mutation_fuzzer.run(yield_negatives=True))
            if inp.oracle == OracleResult.FAILING:
                positive_inputs.add(inp)
            else:
                negative_inputs.add(inp)
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

def main():
    from dbgbench.subjects import Genson120
    bugs = [Genson120]

    for bug_type in bugs:
        genson_grammar = get_genson_grammar_path()
        grammar, _ = parse(genson_grammar)
  
        with bug_type() as bug:
            bug: GensonBug
            samples_paths = bug.sample_files()
            samples = [file.read_text() for file in samples_paths]
            result = bug.execute_samples(samples)
        

        test_inputs = []
        for inp, oracle in result:
            oracle_bool = True if oracle == OracleResult.FAILING else False
            test_inputs.append((escape_non_ascii_utf8(inp), oracle_bool))

        
        initial_inputs = set()
       
        for inp, oracle in test_inputs:
            initial_inputs.add(FandangoInput.from_str(grammar, inp, oracle))
            print(inp)
        
        for inp in initial_inputs:
            inp: FandangoInput
            print(inp, inp.oracle)

        pos_inputs, neg_inputs = generate_more_failing(bug_type, grammar, initial_inputs)

        print(f"Positive inputs: {len(pos_inputs)}")
        print(f"Negative inputs: {len(neg_inputs)}")

if __name__ == "__main__":
    random.seed(2)
    
    main()
