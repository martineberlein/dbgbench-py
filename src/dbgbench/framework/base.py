import tempfile
import logging
import pandas as pd
import subprocess
import io
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from dbgbench.framework.bug_class import Bug
from dbgbench.framework.docker import DBGBenchContainer
from dbgbench.framework.oraclesresult import OracleResult
from dbgbench.framework.util import escape_non_ascii_utf8, unescape_hex_utf8


class DbgbenchBug(Bug, ABC):
    """
    Base class for a dbgbench bug/subject running inside a Docker container.
    """

    def __init__(self, bug_id, oracle):
        super().__init__()
        self._bug_id = bug_id
        self._oracle = oracle

        self._container = None

    def subject(self) -> str:
        return self._bug_id

    def __enter__(self):
        self._ensure_container_started()
        return self

    @abstractmethod
    def grammar_file(self) -> Path:
        """:return the path to the grammar to be used."""
        raise NotImplementedError()

    def sample_inputs(self, get_all=False) -> list[str]:
        """A function which returns the sample inputs (as strings) to work with for this bug."""
        return [escape_non_ascii_utf8(file.read_text()) for file in self.sample_files(get_all=get_all)]

    @abstractmethod
    def sample_files(self, get_all=False) -> list[Path]:
        """A function which returns the sample files to work with for this bug."""
        raise NotImplementedError()

    def suffix(self) -> str:
        return ".cli"

    @abstractmethod
    def _setup_container_files(self):
        """
        Hook for child classes to copy specialized runner scripts or
        other needed files into the container once it's started.
        """
        pass

    @abstractmethod
    def _sample_runner_path(self) -> str:
        """
        Return the path to the script that will execute samples in the container.
        """
        pass

    def tear_down(self):
        """
        Cleanup after ourselves.
        """
        logging.info("Tearing down Dbgbench bug environment.")
        if self._container is not None:
            self._container.stop()

    def _ensure_container_started(self):
        """
        Create and start the container if not already done.
        """
        if self._container is None:
            # By convention, remove .suffix from subject
            short_subject = self._bug_id.split('.', maxsplit=1)[0]
            name = f"dbgbench_{self._bug_id}_{uuid.uuid4()}"
            self._container = DBGBenchContainer(short_subject, name)
            self._container.start(username="root")
            self._setup_container_files()

    def container(self) -> DBGBenchContainer:
        """
        Access the underlying container object.
        """
        self._ensure_container_started()
        return self._container

    def execute_samples_dir(self, sample_dir: Path):
        self._ensure_container_started()
        logging.info("Executing samples in {}".format(sample_dir))

        files = []
        for file in sample_dir.iterdir():
            if file.is_file():
                files.append(file)

        if 0 != len(list(sample_dir.iterdir())):
            self.container().copy_into(files, self.container().container_root_dir("root") / "alhazen_samples")
            return self._execute_samples_in_container()
        return self._empty_result_df()


    def execute_samples(self, test_inputs: list[str]):
        self._ensure_container_started()
        logging.info("Executing samples with oracle.")

        mapping = dict()
        # Create temporary directory for sample files
        with tempfile.TemporaryDirectory() as tmp_dir:
            samples_dir = Path(tmp_dir)
            samples_dir.mkdir(exist_ok=True)

            # Write each test string to a separate file
            for idx, content in enumerate(test_inputs):
                sample_file = samples_dir / Path(f"sample_{idx}.cli")
                sample_file.write_text(unescape_hex_utf8(content), encoding="utf-8")
                mapping[sample_file.name] = content

            # Now call the existing execute_samples method on the temp directory
            data = self.execute_samples_dir(samples_dir)

            result = []
            for _, row in data.iterrows():
                inp_str = mapping[row["file"]]
                oracle = row["oracle"] if [row["input"]] else OracleResult.UNDEFINED
                result.append((inp_str, oracle))

        return result

    def execute_sample(self, test_input: str) -> OracleResult:
        _, oracle = self.execute_samples([test_input])[0]
        return oracle

    # def execute_sample_list(self, sample_files: list[Path]) -> pd.DataFrame:
    #     """
    #     Alternative method if we have a list of sample files rather than one directory.
    #     """
    #     self._ensure_container_started()
    #
    #     if not sample_files:
    #         return self._empty_result_df()
    #
    #     target_dir = self.container().container_root_dir("root") / "alhazen_samples" / "samples"
    #     self.container().check_output(["mkdir", "-p", str(target_dir)])
    #     self.container().copy_into(sample_files, target_dir, username="root")
    #     return self._execute_samples_in_container(exec_dir=target_dir)

    def _execute_samples_in_container(self) -> pd.DataFrame:
        output = b""
        try:
            output = self.container().check_output(["python3",
                                                    self._sample_runner_path(),
                                                    self.subject(),
                                                    (self.container().container_root_dir(
                                                        "root") / "alhazen_samples").resolve(), "rm"])
            prefix = "# csv #- "
            text = output.decode()
            lines = [line[len(prefix):] for line in text.split('\n') if line.startswith(prefix)]
            df = pd.read_csv(io.StringIO("\n".join(lines)), keep_default_na=False, lineterminator='\n')
            df["oracle"] = df.apply(lambda r: self._oracle.apply_oracle(self, r), axis=1)
            return df
        except subprocess.CalledProcessError as ex:
            logging.exception("Process failed")
            logging.error(ex.output)
            raise
        except:
            logging.exception("Process failed")
            logging.error(output.decode())
            raise

    @staticmethod
    def _empty_result_df() -> pd.DataFrame:
        """
        Helper to create an empty DataFrame with the correct columns.
        """
        return pd.DataFrame(columns=["file", "line", "subject", "return code", "output", "oracle"])

