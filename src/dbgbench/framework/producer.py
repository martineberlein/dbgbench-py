import uuid
import logging
import os
from abc import ABC, abstractmethod

from pathlib import Path
from dbgbench.framework.docker import Container, ProducerContainer
from dbgbench.framework import external_exec as execute

class Producer(ABC):

    def __init__(self, name):
        super().__init__()
        self._name = name
        self._container = None
        self._run_script_in_container_path = None
        self._producer_image_name = None
        self._install_script_path = None
        self._host_output_path = None
        
    
    def __enter__(self):
        self._ensure_container_started()
        return self
    
    @abstractmethod
    def _setup_container(self):
        """
        Hook for child classes to copy specialized runner scripts or
        other needed files into the container once it's started.
        """
        pass

    @abstractmethod
    def _get_dockerfile(self):
        pass

    def container(self) -> Container:
        """
        Access the underlying container object.
        """
        self._ensure_container_started()
        return self._container
    
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
            image_file = self._get_dockerfile()
            name = f"producer_{self._name}_{uuid.uuid4()}"
            self._container = ProducerContainer(image_file, name, self._name, self._install_script_path)
            self._container.start()
            self._setup_container()

    
    def run(self) -> Path:
        if not self.container().is_running():
            raise RuntimeError("The container of the producer is not running")
        
        #TODO: überprüfen ob alle datein richtig aufgestezt wurden??

        
        #Führt das script aus welches 
        #TODO: die venv entfernen docker container an sich ist ja abkapselug genug??!
        cmd = ["/root/Desktop/evogfuzz/venv/bin/python", "/root/Desktop/scripts/main.py"]
        self.container().run_in_container(cmd)
        #cmd = ["python3", self._run_script_path]
        #self.container().run_in_container(cmd)
        self.container().copy_to_host(Path("/root/Desktop/output/out.txt"), self._host_output_path)
        return os.path.join(self._host_output_path, "out.txt")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tear_down()