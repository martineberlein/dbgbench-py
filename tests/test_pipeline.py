import unittest

from dbgbench.framework.oraclesresult import OracleResult
from dbgbench.framework.pipeline import ProducerConsumerPipeline
from dbgbench.resources.producer.evogfuzz.evogfuzz_producer import EvoGFuzzProducer
from dbgbench.subjects.calculator import CalculatorBug

class PipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._producer = EvoGFuzzProducer()
        cls._consumer = CalculatorBug()
        

    def test_pipeline(self):
        pipe = ProducerConsumerPipeline(
            producer=self._producer,
            consumer=self._consumer
        )

        result = pipe.run()

        for inp, oracle in result:
            print(inp.ljust(80), oracle, "\n")

    

if __name__ == "__main__":
    unittest.main()