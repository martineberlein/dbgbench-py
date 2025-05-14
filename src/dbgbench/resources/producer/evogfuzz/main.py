"""
This file is supposed to be copied into the container 
and then executed there for producing inputs
"""
import json
import importlib.util
from pathlib import Path

from evogfuzz.evogfuzz_class import EvoGFuzz
from debugging_framework.types import Grammar


def load_grammar(path: Path) -> Grammar:
    with path.open("r") as f:
        return json.load(f)


def load_inputs(path: Path) -> list[str]:
    with path.open("r") as f:
        return [line.strip() for line in f if line.strip()]


def load_oracle(path: Path):
    spec = importlib.util.spec_from_file_location("oracle_module", path)
    oracle_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle_module)
    return oracle_module.oracle  # expects `def oracle(inp: str) -> tuple[OracleResult, Optional[Exception]]`


def main():
    input_dir = Path("/root/Desktop/input")
    output_file = Path("/root/Desktop/output/out.txt")

    grammar = load_grammar(input_dir / "grammar.json")
    inputs = load_inputs(input_dir / "inputs.txt")
    oracle = load_oracle(input_dir / "oracle.py")
    print(grammar)
    for inp in inputs:
        print(inp)
        print(type(inp))

    print(oracle)
    print(type(oracle))
    fuzzer = EvoGFuzz(grammar=grammar, oracle=oracle, inputs=inputs)
    found = fuzzer.fuzz()

    with output_file.open("w") as f:
        for inp in list(found)[:20]:
            f.write(str(inp) + "\n")


if __name__ == "__main__":
    main()