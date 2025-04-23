import tempfile
import logging
import pandas as pd
import subprocess
import io
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from dbgbench.framework.bug_class import Bug
from dbgbench.framework.docker import Container
from dbgbench.framework.oraclesresult import OracleResult
from dbgbench.framework.oracles import Oracle

from . import external_exec as execute

import json

class JavaBug(Bug, ABC):
    """
    Base class for a java bug/subject running inside a Docker container
    """
    def __init__(self, bug_id: str, oracle: Oracle):
        super().__init__()
        self._bug_id = bug_id
        self._oracle = oracle

        self._container = None
        self._jar = None

    def __enter__(self):
        self._ensure_container_started()
        return self
    
    def subject(self) -> str:
        return self._bug_id
    
    @abstractmethod
    def _setup_container_files(self):
        """
        Hook for child classes to copy specialized runner scripts or
        other needed files into the container once it's started.
        Not needed if the files get already copied in the dockerfile.
        """
        pass

    @abstractmethod
    def _get_dockerfile_dir(self) -> Path:
        """
        Hook for child classes to insert dockerfile.
        Needed for creating the container.
        """
        pass
    
    def tear_down(self):
        """
        Cleanup after ourselves.
        """
        logging.info("Tearing down Java bug environment.")
        if self._container is not None:
            self._container.stop()

    def _ensure_container_started(self):
        """
        Create and start the container if not already done.
        """
        if self._container is None:
            name = f"javabug_{self._bug_id}_{uuid.uuid4()}"
            docker_dir = self._get_dockerfile_dir()
            self._container = Container(docker_dir, name)
            self._container.start()
            self._setup_container_files()

    def container(self) -> Container:
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
            self.container().copy_into(files, self.container().container_root_dir("root") / "samples")
            return self._execute_samples_in_container()
        return self._empty_result_df()
    
    def execute_samples(self, test_inputs: list[str]) -> list[tuple[str, OracleResult]]:
        self._ensure_container_started()
        logging.info("Executing JavaBug samples with oracle")

        mapping = dict()
        # Create temporary directory for sample files
        with tempfile.TemporaryDirectory() as tmp_dir:
            samples_dir = Path(tmp_dir)
            samples_dir.mkdir(exist_ok=True)

            # Write each test string to a separate file
            for idx, content in enumerate(test_inputs):
                sample_file = samples_dir / Path(f"sample_{idx}.json")
                sample_file.write_text(content, encoding="utf-8")
                mapping[sample_file.name] = content

            # Now call the existing execute_samples method on the temp directory
            data = self.execute_samples_dir(samples_dir)

            result = []
            #Failing Samples
            for _, row in data.iterrows():
                inp_str = mapping[row["file"]]
                oracle = row["oracle"]
                #removing failing sample from mapping
                mapping.pop(row["file"])
    
                result.append((inp_str, oracle))
            
            #Passing Samples (habe es an die Stelle gemach weil wir die Info aller samples in _exectute_samples_in_container nicht haben)
            for _, inp_str in mapping.items():
                result.append((inp_str, OracleResult.PASSING))
                
        return result
        
    def _execute_samples_in_container(self) -> pd.DataFrame:
        output = b""
        try:
            output = self.container().check_output(["java",
                                                    "-jar",
                                                    self._jar,
                                                    "--ignore-exceptions",
                                                    "--log-exceptions",
                                                    "./exception_log/exceptions.json",
                                                    "./samples"])
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                proc = execute.run(["docker", "cp", f"{self.container().name}:root/Desktop/exception_log/exceptions.json", tmp_dir], 
                                   None
                                )
                proc.check_returncode()
                with open(f"{tmp_dir}/exceptions.json") as f:
                    exceptions = json.load(f)
                    #fastest approach to build the df 
                    # https://stackoverflow.com/questions/10715965/create-a-pandas-dataframe-by-appending-one-row-at-a-time
                    rows_list = []
                    for exception in exceptions:
                        for file in exception["files"]:
                            tmp = {"file": file, 
                                "exception": exception["name"], 
                                "oracle": self._oracle.apply_oracle(self, exception["name"])
                                }
                            rows_list.append(tmp)
                    df = pd.DataFrame(rows_list)

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

