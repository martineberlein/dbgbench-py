from pathlib import Path

from dbgbench.framework.java_bug import JavaBug
from dbgbench.framework.oracles import FindWrapper
from dbgbench.resources import get_genson_samples, get_genson_grammar_path, get_genson_dockerfile, get_genson_samples_dir, get_genson_subject_jar


class GensonBug(JavaBug):
    """
    Concrete bug class specialized for genson.
    """

    def __init__(self, bug_id, oracle):
        #TODO: oracle anpassen
        super().__init__(bug_id, oracle)

    def _get_dockerfile_dir(self) -> Path:
        return get_genson_dockerfile()
    
    def suffix(self) -> str:
        return ".json"

    def grammar_file(self) -> Path:
        """:return the path to the grammar to be used."""
        return get_genson_grammar_path()

    def sample_files(self, get_all=False) -> list[Path]:
        """A function which returns the sample files to work with for this bug."""
        sample_dir = get_genson_samples_dir()
        if get_all:
            return [file for file in sample_dir.iterdir() if file.is_file()]

        files = []
        for file in sample_dir.iterdir():
            if file.is_file() and (file.name.endswith("benign" + self.suffix()) or file.name == self._bug_id + self.suffix()):
                files.append(file)
        return files

    def _setup_container_files(self):
        """
        Copy genson subject jar into container.
        """
        jar_path = get_genson_subject_jar()
        self.container().copy_into(
            [jar_path],
            Path("/root/Desktop/genson"),
            username="root"
        )

    #not sure yet if needed
    #@staticmethod
    #def _sample_runner_path() -> str:
    #    """
    #    Return the path of the specialized runner script for find.
    #    """
    #    return "/root/Desktop/alhazen_scripts/sample_runner_find.py"