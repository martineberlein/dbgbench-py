from pathlib import Path

import tempfile
import pkgutil
import logging

from . import external_exec as execute


feature_flags = ["--length",
                 "--present-absent",
                 "--charInterpretation",
                 "--numericInterpretation"]


def run_java(cmd, logfile, check=True, **kwargs):
    call_java(cmd, logfile, check=check, **kwargs)


def call_java(cmd, logfile, **kwargs):
    cmd = execute.make_cmd(cmd)
    try:
        if "timeout" not in kwargs:
            kwargs["timeout"] = 3600
        # , "-XX:+HeapDumpOnOutOfMemoryError"
        execute.run(["java", "-Xss1g", "-Xmx10g"] + cmd, logfile, **kwargs)
    finally:
        logging.info("Stopped {}".format(cmd))
        if "cwd" in kwargs:
            clear_failed_java(kwargs["cwd"])
        else:
            clear_failed_java(Path("."))


def clear_failed_java(cwd):
    for dump in cwd.glob("*.dmp"):
        dump.unlink()
    for dump in cwd.glob("*.phd"):
        dump.unlink()
    for dump in cwd.glob("*.trc"):
        dump.unlink()


def grammar_rewrite(grammarfile, sample, target_dir, logfile):
    new_grammarfile = target_dir / (grammarfile.stem + ".scala")

    target_dir.mkdir(parents=True)

    cmd = ["-jar", str(parserjar.parser_jar()),
           "-gc", (target_dir / "grammar-cache"),
           "-g", grammarfile.resolve(),
           "substrGrammar",
           "-s", str(sample.resolve()),
           "-o", str(target_dir.resolve() / "depth.csv"),
           "-go", str(new_grammarfile.resolve())] + feature_flags
    run_java(cmd, logfile, cwd=target_dir)
    return new_grammarfile, target_dir.resolve() / "depth.csv"


def feature_file(grammarfile, target_dir, logfile):
    new_grammarfile = target_dir / grammarfile.name

    target_dir.mkdir(parents=True)

    cmd = ["-jar", str(parserjar.parser_jar()),
           "-gc", (target_dir / "grammar-cache"),
           "-g", str(grammarfile.resolve()),
           "feature-file",
           "-o", str(target_dir.resolve() / "depth.csv"),
           "-go", str(new_grammarfile.resolve())] + feature_flags
    run_java(cmd, logfile, cwd=target_dir)
    return new_grammarfile, target_dir.resolve() / "depth.csv"


def run_reach_target(grammarfile, spec_file, feature_file, target_dir, logfile, random_seed, suffix):
    if not target_dir.exists():
        target_dir.mkdir(parents=True)

    cmd = ["-jar", str(parserjar.parser_jar()),
           "-gc", grammarfile.parent / "grammar-cache",
           "-g", str(grammarfile.resolve()),
           "reachTargets",
           "--times", str((target_dir.parent / "times.csv").resolve()),
           "--features", feature_file,
           "--suffix", suffix,
           "--seed", str(random_seed),
           "--target", str(spec_file.resolve()),
           "-o", str(target_dir.resolve()),
           "--max-rule-occurrences", "5"] + feature_flags
    run_java(cmd, logfile, cwd=spec_file.parent, check=True)


# def collect_features(grammarfile: Path, inp_dir: Path, logfile, target_csv, features=None) -> pandas.DataFrame:
#     if features is None:
#         features = extract_features(grammarfile.parent / "depth.csv")
#     feature_names = [f.name() for f in features]
#     # do not run the tool if the feature file is already there
#     if not target_csv.exists():
#         cmd = ["-jar", str(parserjar.parser_jar()),
#                "-gc", str((grammarfile.parent / "grammar-cache").resolve()),
#                "-g", str(grammarfile.resolve()),
#                "countAmbiguous",
#                "-i", str(inp_dir.resolve()),
#                "-o", str(target_csv.resolve())] + feature_flags
#         run_java(cmd, logfile, cwd=Path(target_csv).parent, check=True)
#         # the tool just ran, so the target_csv should be there now
#         assert target_csv.exists()
#     # load the features
#     features_csv = pandas.read_csv(target_csv, index_col="file", keep_default_na=False)
#     # and clean them
#     ff = features_csv[feature_names]
#     # NaN is loaded as a string instead of a value
#     ff = ff.replace("NaN", numpy.nan)
#     # the python part of alhazen can not handle inf values
#     ff = ff.replace(-numpy.inf, numpy.finfo('float32').min)
#     ff = ff.replace(numpy.inf, numpy.finfo('float32').max)
#     # make sure the column type is numeric
#     ff = ff.apply(lambda s: pandas.to_numeric(s, downcast='float'))
#     # apply feature-specific cleaning
#     for feature in features:
#         ff = feature.clean_data(ff)
#     # the kotlin part of alhazen can handle float64, the python part can not
#     for feature in features:
#         ff[feature.name()] = ff[feature.name()].apply(lambda s: min(s, numpy.finfo('float32').max))
#         ff[feature.name()] = ff[feature.name()].apply(lambda s: max(s, numpy.finfo('float32').min))
#     features_csv[feature_names] = ff
#     return features_csv


class ParserJar:
    """
    This class capsulates a jar file which was extracted from the pex, and makes sure it is deleted when alhazen exists.
    """

    def __init__(self):
        self.__parserjar = None

    def __enter__(self):
        assert self.__parserjar is None
        self.__parserjar = tempfile.NamedTemporaryFile(suffix=".jar", delete=False)
        with self.__parserjar as pj:
            pj.write(pkgutil.get_data("alhazen", "parsers.jar"))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self.__parserjar is not None
        # delete the jar file
        Path(self.__parserjar.name).unlink()
        self.__parserjar = None

    def parser_jar(self):
        assert self.__parserjar is not None
        return Path(self.__parserjar.name)


parserjar = ParserJar()
