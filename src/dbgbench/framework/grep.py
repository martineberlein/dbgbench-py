from pathlib import Path

from dbgbench.framework.base import BaseDbgbenchBug
from dbgbench.framework.oracles import GrepWrapper


class GrepBug(BaseDbgbenchBug):
    """
    Concrete bug class specialized for grep.
    """

    def __init__(self, bug_id, oracle):
        super().__init__(bug_id, GrepWrapper(oracle))

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

