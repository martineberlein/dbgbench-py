import re
from abc import *

from .oraclesresult import OracleResult


class Oracle(metaclass=ABCMeta):

    @abstractmethod
    def apply_oracle(self, bug, row):
        pass

    def generate_oracle_data(self, bug, cli):
        pass


def contains_option(line, option):
    return option in line.split(" ")


def contains_option_with_arg(line, search):
    for option in line.split(" "):
        if option.startswith(search):
            return True
    return False


def contains_one_of_option(line, options):
    sline = line.split(" ")
    return any([opt in sline for opt in options])


def find_arg_to(line, options):
    sline = line.split(" ")
    for opt in options:
        try:
            idx = sline.index(opt)
            yield sline[idx+1]
        except ValueError:
            pass


name_pattern = re.compile(b"^[^:]+:", re.MULTILINE)
null_name_pattern = re.compile(b"^[^\\x00]+\\x00", re.MULTILINE)
count_pattern = re.compile(b"^ *[0-9]+\t?\x08?[:\\-]", re.MULTILINE)
null_data_options = ['-z', '--null-data']
supress_output_options = ["-c", "--count",
                          "-L", "--files-without-match",
                          "-l", "--files-with-matches",
                          "-q", "--quiet", "--silent"]
color_pattern = re.compile(b'\x1b\\[[01]*;[0-9][0-9]m')
control_pattern = re.compile(b'\x1b\\[([0-9][0-9])?[Km]')
output_line_number_options = ["-n", "--line-number",
                              "-T",
                              "--null", "-Z"]
output_byte_number_options = ["--byte-offset", "-b", "-u", "--unix-byte-offsets"]
output_line_name_options = ["-H", "--with-filename"]


class GrepWrapper(Oracle):

    def __init__(self, delegate: Oracle):
        self.__delegate = delegate

    def generate_oracle_data(self, bug, cli):
        return self.__delegate.generate_oracle_data(bug, cli)

    def apply_oracle(self, bug, row):
        if "Grep terminated" not in row["output"]:
            return OracleResult.UNDEFINED
        return self.__delegate.apply_oracle(bug, row)


class OutputSubstringOracle(Oracle):

    def __init__(self, substr):
        self.__substr = substr

    def generate_oracle_data(self, bug, cli):
        return ""

    def apply_oracle(self, bug, row):
        if self.__substr in to_bytes(row["output"]):
            return OracleResult.FAILING
        return OracleResult.PASSING


class SegvOracle(Oracle):
    """The rc_oracle considers a run bug-indicating if
        the return code is 139 (segmentation fault)"""

    def generate_oracle_data(self, bug, cli):
        return ""

    def apply_oracle(self, bug, row):
        if row["return code"] == 139 or row["return code"] == 134:
            return OracleResult.FAILING
        return OracleResult.PASSING


class AssertionOracle(Oracle):
    """The rc_oracle considers a run bug-indicating if
        the return code is 134 (assertion violated)"""

    def generate_oracle_data(self, bug, cli):
        return ""

    def apply_oracle(self, bug, row):
        if row["return code"] == 134:
            return OracleResult.FAILING
        return OracleResult.PASSING


class HangOracle(Oracle):
    """The rc_oracle considers a run bug-indicating if
        the return code is 124 (timeout triggered)"""

    def generate_oracle_data(self, bug, cli):
        return ""

    def apply_oracle(self, bug, row):
        if row["return code"] == 124:
            return OracleResult.FAILING
        return OracleResult.PASSING


def to_bytes(inp):
    if inp is None:
        return None
    if isinstance(inp, str):
        if inp.startswith("b'") or inp.startswith('b"'):
            inp = eval(inp)
        else:
            inp = inp.encode('utf-8')
    return inp


def clear_grep(line, output):
    output = output.replace(b'Binary file (standard input) matches\n', b'')
    output = output.replace(b'\nGrep terminated\n', b'')
    if contains_one_of_option(line, output_line_name_options):
        if contains_one_of_option(line, ["--null", "-Z"]):
            output = re.sub(null_name_pattern, b"", output)
        else:
            output = re.sub(name_pattern, b"", output)
    if "--color" in line or '--colour' in line:
        output = re.sub(color_pattern, b'', output)
        output = re.sub(control_pattern, b'', output)
    if contains_one_of_option(line, output_line_number_options):
        output = re.sub(count_pattern, b"", output)
    if contains_one_of_option(line, output_byte_number_options):
        output = re.sub(count_pattern, b"", output)
    return output


class NoNewTextOracle(Oracle):
    """grep cannot generate new characters.
    So, if there is a character in the output that does not occur in the input, that is a bug."""

    def apply_oracle(self, bug, row):
        if row["output"] is None:
            #  return OracleResult.UNDEFINED
            return OracleResult.PASSING
        if contains_one_of_option(row["line"], supress_output_options):
            #  return OracleResult.UNDEFINED
            return OracleResult.PASSING
        if row["return code"] not in [0, 1]:
            #  return OracleResult.UNDEFINED
            return OracleResult.PASSING
        if contains_option_with_arg(row["line"], "\'--label="):
            return OracleResult.PASSING

        inp = to_bytes(row["input"])
        if inp is None:
            #  return OracleResult.UNDEFINED
            return OracleResult.PASSING

        output = clear_grep(row["line"], to_bytes(row["output"]))
        if b'grep: Invalid back reference\n' in output:
            return OracleResult.PASSING
        for c in output[:-1]:  # grep always adds a trailing newline, which we don't want to compare
            if c not in inp:
                return OracleResult.FAILING
        return OracleResult.PASSING


class LineOracle(Oracle):

    def apply_oracle(self, bug, row):
        """grep always generates entire lines of output."""
        if row["output"] is None:
            #  return OracleResult.UNDEFINED
            return OracleResult.PASSING
        if contains_one_of_option(row["line"], ['-L', '-l', '-o', '--only-matching']):
            #  return OracleResult.UNDEFINED
            return OracleResult.PASSING
        if contains_one_of_option(row["line"], supress_output_options):
            #  return OracleResult.UNDEFINED
            return OracleResult.PASSING
        if row["return code"] not in [0, 1]:
            #  return OracleResult.UNDEFINED
            return OracleResult.PASSING
        if contains_option_with_arg(row["line"], "\'--label="):
            return OracleResult.PASSING

        inp = to_bytes(row["input"])
        if inp is None:
            #  return OracleResult.UNDEFINED
            return OracleResult.PASSING
        inp = inp.splitlines()

        output = clear_grep(row["line"], to_bytes(row["output"]))
        if b'grep: Invalid back reference\n' in output:
            return OracleResult.PASSING
        for outline in output[:-1].splitlines():  # grep always adds a new line or separator in the end
            if outline not in inp:
                return OracleResult.FAILING
        return OracleResult.PASSING


class NoNewLineOracle(Oracle):

    def generate_oracle_data(self, bug, cli):
        return ""

    def apply_oracle(self, bug, row):
        end = b'\n'[0]
        if contains_one_of_option(row['line'], null_data_options):
            end = b'\x00'[0]
        output = row["output"]
        output = to_bytes(output).replace(b"\nGrep terminated\n", b"")
        if output.startswith(b'grep:'):
            return OracleResult.PASSING
        if 0 != len(output) and output[-1] != end:
            return OracleResult.FAILING
        return OracleResult.PASSING
