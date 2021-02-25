from typing import Union
import unittest
from .test_base import TestBase


class TestSciHub(TestBase):
    def test_print(self):
        self.logger.debug("hello")

    def test_end(self):
        self.logger.debug("end")


if __name__ == "__main__":
    unittest.main(verbosity=2)
