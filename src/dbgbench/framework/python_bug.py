import tempfile
import logging
import os
import uuid
import pandas as pd

from abc import ABC, abstractmethod
from pathlib import Path

from dbgbench.framework.bug_class import Bug
from dbgbench.framework.docker import Container
from dbgbench.framework.oraclesresult import OracleResult

class PythonBug(Bug, ABC):
    """
    Base class for a java bug/subject running inside a Docker container.
    Not perfect.
    At the moment just copies files into container, executes them with an oracle inside the container.
    Gets the output back as DataFrame.
    Problem is we dont know atm how the faulty python files need their inputs and produce the outputs.
    """
    def __init__(self, bug_id: str):
        super().__init__()
        self._bug_id = bug_id

        self._container = None
        self._faulty_py = None

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
            name = f"pythonbug_{self._bug_id}_{uuid.uuid4()}"
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
    
    def execute_samples(self, test_inputs: list[str]) -> list[tuple[str, OracleResult]]:
        self._ensure_container_started()
        logging.info("Executing PythonBug samples with oracle")

        #Copies the test_inputs into the container for execution
        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(os.path.join(tmp_dir, "in.txt"), "w") as tmp_in:
                tmp_in.writelines(test_inputs)
                tmp_in.flush()
                self.container().copy_into([Path(tmp_in.name)], "/root/Desktop/input/")

        #Executes the bug with the inputs in the container
        self.container().check_output(["python3", "/root/Desktop/scripts/main.py"])
        
        #TODO: Wir verlieren hier momentan den Error 
        #parses the results from the container into a list[tuple[test_input, oracle_result]]
        results = []
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.container().copy_to_host(Path("/root/Desktop/output/out.txt"), Path(tmp_dir))
            out_file = Path(tmp_dir, "out.txt")
            with open(out_file, "r") as file:
                for line in file.readlines():
                    input_str, result_str, error_str = line.split(",")
                    result = OracleResult.FAILING if "FAILING" in result_str else OracleResult.PASSING
                    results.append((input_str, result))
        
        return results


    #TODO: Wenn Martin es als DataFrame haben will, 
    # könnte man das im container noch als dataframe parsen in die out.txt und diese dann hier nur wieder einlesen
    @staticmethod
    def _empty_result_df() -> pd.DataFrame:
        """
        Helper to create an empty DataFrame with the correct columns.
        """
        return pd.DataFrame(columns=["input", "oracle", "exception"])

