import subprocess
import pandas
import json
import typing
import numpy
from pathlib import Path
from abc import abstractmethod

from itertools import zip_longest

from .oraclesresult import OracleResult
from .tools import call_java
from .bug_class import Bug


def grouper(iterable, n):
    args = [iter(iterable)] * n
    return [[c for c in chunk if c is not None] for chunk in zip_longest(*args)]


class JavaBug(Bug):

    def __init__(self, error):
        super().__init__()
        self.__error = error

    @abstractmethod
    def subject_jar(self) -> Path:
        """:return the jar file to be invoked."""
        raise AssertionError("Overwrite in subclass.")

    def execute_sample_list(self, execdir, samples):
        jarfile = self.subject_jar()
        exception_log = execdir / "exceptions.log"
        execution_log = execdir / "execution.log"

        per_chunk = []
        for chunk in grouper(samples, 100):
            cmd = ["-jar", jarfile,
                   "--ignore-exceptions",
                   "--log-exceptions", exception_log] + chunk
            call_java(cmd, execution_log, cwd=execdir)

            exceptions_data = self.__read_exceptions(exception_log)
            all_data = self.__sample_frame(chunk)

            joined = exceptions_data.set_index("file") \
                .join(all_data.set_index("file"), how='outer') \
                .reset_index()
            per_chunk.append(self.__apply_oracle(joined))
        return pandas.concat(per_chunk)

    def execute_samples(self, sample_dir):
        jarfile = self.subject_jar()
        exception_log = sample_dir.parent / "exceptions.log"
        execution_log = sample_dir.parent / "execution.log"

        cmd = ["-jar", str(jarfile.resolve()),
               "--ignore-exceptions",
               "--log-exceptions", str(exception_log.resolve()), str(sample_dir.resolve())]
        call_java(cmd, execution_log, cwd=sample_dir.parent)

        exceptions_data = self.__read_exceptions(exception_log)
        all_data = self.__sample_frame(sample_dir.iterdir())

        joined = exceptions_data.set_index("file") \
            .join(all_data.set_index("file"), how='outer') \
            .reset_index()
        joined["output"] = joined["output"].fillna("")
        return self.__apply_oracle(joined)

    def __sample_frame(self, samples: typing.Generator[Path, None, None]) -> pandas.DataFrame:
        all_data = []
        for file in samples:
            all_data.append({
                "file": str(file.name),
                "subject": self.subject()
            })
        if 0 == len(all_data):
            return pandas.DataFrame(columns=["file", "line", "subject"])
        return pandas.DataFrame.from_records(all_data)

    def __read_exceptions(self, exception_log: Path):
        if not exception_log.exists():
            return pandas.DataFrame(columns=["file", "output"])
        else:
            with open(exception_log, 'r') as except_in:
                exceptions = json.load(except_in)
            exceptions_data = []
            for exp in exceptions:
                stack_hash = exp["stack_hash"]
                for file in exp["files"]:
                    exceptions_data.append({
                        "file": Path(file).name,
                        "output": stack_hash
                    })
            exceptions_data = pandas.DataFrame.from_records(exceptions_data)
            return exceptions_data

    def __apply_oracle(self, exceptions_data):
        exceptions_data["oracle"] = numpy.where(exceptions_data["output"] == self.__error,
                                                OracleResult.BUG,
                                                OracleResult.NO_BUG)
        return exceptions_data
