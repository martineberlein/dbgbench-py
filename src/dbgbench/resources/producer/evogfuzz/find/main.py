from evogfuzz.evogfuzz_class import EvoGFuzz
from dbgbench.subjects import Find07b941b1, Find091557f6, Finddbcb10e9, Findff248a20
from dbgbench.resources.dict_grammar.find_grammar import find_grammar
from debugging_framework.fuzzingbook.grammar import is_valid_grammar

def main():
    with Find07b941b1() as bug:
        inputs = ["timeout 0.5s find -regex '.*'"]
        fuzzer = EvoGFuzz(find_grammar, bug.execute_sample, [])
        found = fuzzer.fuzz()

        #with output_file.open("w") as f:
        for inp in list(found):
            print(str(inp) + f"{inp.__oracle}\n")



if __name__ == "__main__":
    main()