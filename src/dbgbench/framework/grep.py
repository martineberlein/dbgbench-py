from pathlib import Path

from .common import DbgbenchBug
from .oracles import GrepWrapper

class GrepBug(DbgbenchBug):

    def __init__(self, bugnr, oracle):
        super(GrepBug, self).__init__(bugnr, GrepWrapper(oracle))

    def _container_setup(self):
        # get the script files in place
        self.container().copy_into(
            [Path(__file__).parent.parent / "resources" /"sample_runner_grep.py"],
            Path("/root/Desktop/alhazen_scripts"), username="root")

    def _sample_runner(self):
        return "/root/Desktop/alhazen_scripts/sample_runner_grep.py"
