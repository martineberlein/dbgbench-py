from pathlib import Path

from dbgbench.framework.base import DbgbenchBug
from dbgbench.framework.oracles import GrepWrapper
from dbgbench.resources import get_grep_grammar_path, get_grep_samples_dir


class GrepBug(DbgbenchBug):
    """
    Concrete bug class specialized for grep.
    """

    def __init__(self, bug_id, oracle):
        super().__init__(bug_id, GrepWrapper(oracle))

    def grammar_file(self) -> Path:
        """:return the path to the grammar to be used."""
        return get_grep_grammar_path()

    def sample_files(self, get_all=False) -> list[Path]:
        """A function which returns the sample files to work with for this bug."""
        sample_dir = get_grep_samples_dir()
        if get_all:
            return [file for file in sample_dir.iterdir() if file.is_file()]

        files = []
        for file in sample_dir.iterdir():
            if file.is_file() and (file.name.endswith("benign" + self.suffix()) or file.name == self._bug_id + self.suffix()):
                files.append(file)
        return files

    def _setup_container_files(self):
        """
        Copy specialized runner for grep into the container.
        """
        script_path = Path(__file__).parent.parent / "resources" / "sample_runner_grep.py"
        self.container().copy_into(
            [script_path],
            Path("/root/Desktop/alhazen_scripts"),
            username="root"
        )

    @staticmethod
    def _sample_runner_path() -> str:
        """
        Return the path of the specialized runner script for grep.
        """
        return "/root/Desktop/alhazen_scripts/sample_runner_grep.py"

