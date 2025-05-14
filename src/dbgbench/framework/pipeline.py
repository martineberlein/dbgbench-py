from dbgbench.framework.producer import Producer
from dbgbench.framework.bug_class import Bug
from pathlib import Path
# Producer produziert eine str liste
# Consumer aka Bug nimmt diese einfach als samples bug.execute(samples)
# und diese werden als wieder neue file im gleichen ordner als results.txt gespeichert

# REFAKTORING!

class ProducerConsumerPipeline():
    def __init__(self, producer: Producer, consumer: Bug):
        self._producer = producer
        self._consumer = consumer

    def run(self) -> Path:
        """
        Executes the pipeline and gives back the path of the output of the consumer
        """
        host_output_path = self._producer.run()
        with open(host_output_path, "r") as f:
            samples = f.readlines()

        return self._consumer.execute_samples(samples)

        

    
    