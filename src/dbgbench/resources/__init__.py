import importlib.resources as pkg_resources


def get_grep_grammar_path():
    return pkg_resources.files("dbgbench.resources.fandango") / "grep.fan"


def get_grep_samples_dir():
    return pkg_resources.files("dbgbench.resources.samples") / "grep"

def get_grep_samples():
    sample_dir = get_grep_samples_dir()
    return [file.read_text() for file in sample_dir.iterdir() if file.is_file()]


def get_islearn_pattern_file_path():
    return pkg_resources.files("dbgbench.resources") / "patterns_islearn.toml"
