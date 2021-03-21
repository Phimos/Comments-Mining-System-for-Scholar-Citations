import json
import unittest

from ..crawlers.collector import PaperCollector
from .test_base import TestBase


class TestCollector(TestBase):
    collector = PaperCollector()
    with open("./citeminer/configs/basic.json") as infile:
        config = json.load(infile)
    collector.init_from_config(config)

    def test_collect_metadata(self):
        self.collector.collect_metadata()

    def test_collect_pdf(self):
        pass
