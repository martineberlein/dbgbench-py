from pathlib import Path

from dbgbench.framework.producer import Producer
from dbgbench.resources import get_ubuntu_dockerfile


class FandangoProducer(Producer):

    def __init__(self, ):
        super().__init__("Fandango")
        self._host_install_script_path = Path("src/dbgbench/resources/producer/evogfuzz/install.sh").resolve()
        self._host_output_path = Path("src/dbgbench/resources/producer/evogfuzz").resolve()

        #Diese Paths können je nach Anwendungsfall angepasst werden 
        # und werden zum fuzzen von Inputs mit EvoGFuzz benötigt!
        self._host_run_script_path = Path("src/dbgbench/resources/producer/evogfuzz/main.py").resolve()
        self._host_grammar_path = Path("src/dbgbench/resources/producer/evogfuzz/calculator/grammar.json").resolve()
        self._host_inputs_path = Path("src/dbgbench/resources/producer/evogfuzz/calculator/inputs.txt").resolve()
        self._host_oracle_path = Path("src/dbgbench/resources/producer/evogfuzz/calculator/oracle.py").resolve()

    
    def _get_dockerfile(self):
        return get_ubuntu_dockerfile()
    
    def _setup_container(self): 
        #Copies the main.py script into the container
        self.container().copy_into(dst_path=self.container().container_root_dir("root") / "scripts", 
                                   local_paths=[self._host_run_script_path])

        self._container_run_script_path = self.container().container_root_dir("root") / "scripts" / "main.py"

        #Copies the grammar, sample inputs and oracle into the container
        self.container().copy_into(dst_path=self.container().container_root_dir("root") / "input", 
                                   local_paths=[self._host_grammar_path, self._host_inputs_path, self._host_oracle_path])
        
    
if __name__ == "__main__":

    with EvoGFuzzProducer() as producer:
        producer.run()