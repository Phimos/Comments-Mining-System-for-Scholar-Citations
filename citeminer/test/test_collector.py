import unittest
from .test_base import TestBase
from ..crawlers.collector import PaperCollector
import json


class TestCollector(TestBase):
    collector = PaperCollector()
    with open("./configs/basic.json") as infile:
        config = json.load(infile)
    collector.init_from_config(config)

    def test_collect_metadata(self):
        self.collector.collect_metadata()

    def test_collect_pdf(self):
        pass