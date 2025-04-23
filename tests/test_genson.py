import unittest

from fdlearn.interface.fandango import parse

from dbgbench.framework.oraclesresult import OracleResult
from dbgbench.resources import (get_genson_dockerfile, 
                                get_genson_grammar_path,
                                get_genson_subject_jar,
                                get_genson_samples)
from dbgbench.framework.grep import GrepBug
from dbgbench.framework.find import FindBug
from dbgbench.subjects import *


class BugsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
        #genson
        #genson_grammar_path = get_genson_grammar_path()
        #cls.genson_gramar, cls.genson_constraints = parse(genson_grammar_path)
        #cls.genson_samples = get_genson_samples()

    def test_get_genson_dockerfile(self):
        print(get_genson_dockerfile())

    def test_get_genson_samples(self):
        print(get_genson_samples())

    def test_get_genson_jar(self):
        print(get_genson_subject_jar())

if __name__ == "__main__":
    unittest.main()