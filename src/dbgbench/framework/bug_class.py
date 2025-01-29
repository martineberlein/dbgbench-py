from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator
from pandas import DataFrame
from typing import Union
import importlib
import sys
from typing import Any

# from . import oracles


class Bug(ABC):

    @abstractmethod
    def subject(self) -> str:
        """:return a name for the program under test"""
        raise AssertionError("Overwrite in subclass.")

    @abstractmethod
    def grammar_file(self) -> Path:
        """:return the path to the grammar to be used."""
        raise AssertionError("Overwrite in subclass.")

    @abstractmethod
    def sample_files(self) -> Generator[Path, None, None]:
        """A generator methods which yields the sample files to work with for this bug."""
        raise AssertionError("Overwrite in subclass.")

    def tear_down(self):
        """You can overwrite this if there is some cleanup to be done after an alhazen run for this bug."""
        pass

    def suffix(self) -> str:
        """:return the suffix for input files for this program under test."""
        g = self.sample_files()
        sample = next(g)
        return sample.suffix

    def execute_samples(self, sample_dir) -> DataFrame:
        """helper method to execute all samples in a given directory."""
        raise NotImplementedError("Overwrite in subclass.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tear_down()
