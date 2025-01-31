from os.path import samestat

from dbgbench.framework.oraclesresult import OracleResult
from dbgbench.resources import get_grep_grammar_path, get_grep_samples
from dbgbench.framework.util import escape_non_ascii_utf8
from dbgbench.subjects import Grep3c3bdace, Grepc96b0f2c

from fandangoLearner.interface.fandango import parse
from fandangoLearner.data.input import FandangoInput
from fandangoLearner.learner import FandangoLearner
from fandangoLearner.logger import LoggerLevel
from fandangoLearner.resources.patterns import Pattern
from fandangoLearner.refinement.mutation import MutationFuzzer


def generate_more_failing(bug_type_, grammar_, samples_):

    def bug_oracle(inp):
        with bug_type_() as bug:
            res = bug.execute_sample(str(inp))
        return res

    samples_ = [
        FandangoInput.from_str(grammar_, escape_non_ascii_utf8(inp), bug_oracle(inp)) for inp in samples_
    ]

    seeds = [inp for inp in samples_ if inp.oracle == OracleResult.FAILING]

    mutation_fuzzer = MutationFuzzer(grammar_, seed_inputs=seeds, oracle=bug_oracle)

    for inp in list(mutation_fuzzer.run()):
        print(inp)


if __name__ == "__main__":
    bug_type = Grepc96b0f2c

    grep_grammar = get_grep_grammar_path()
    grammar, _ = parse(grep_grammar)

    generate_more_failing(bug_type, grammar, get_grep_samples())

    samples = get_grep_samples()
    with bug_type() as bug:
        result = bug.execute_samples(samples)

    test_inputs = []
    for inp, oracle in result:
        oracle_bool = True if oracle == OracleResult.BUG else False
        test_inputs.append((escape_non_ascii_utf8(inp), oracle_bool))

    initial_inputs = {
        FandangoInput.from_str(grammar, inp, oracle) for inp, oracle in test_inputs
    }

    additional_inputs = []
    for _ in range(100):
        additional_inputs.append(str(grammar.fuzz(max_nodes=100)))

    with bug_type() as bug:
        result = bug.execute_samples(additional_inputs)

    test_inputs = []
    for inp, oracle in result:
        oracle_bool = True if oracle == OracleResult.BUG else False
        test_inputs.append((inp, oracle_bool))

    add_initial_inputs = {
        FandangoInput.from_str(grammar, inp, oracle) for inp, oracle in test_inputs
    }
    initial_inputs.update(add_initial_inputs)


    patterns = [
        Pattern(
            string_pattern="exists <elem> in <NON_TERMINAL>: is_inside(<elem>, <start>);",
        ),
        # Pattern(
        #     string_pattern="str(<NON_TERMINAL>) == <STRING>;",
        # )
    ]

    learner = FandangoLearner(grammar, patterns=patterns, logger_level=LoggerLevel.INFO)

    learned_constraints = learner.learn_constraints(
        initial_inputs
    )

    for constraint in learned_constraints:
        print(constraint)