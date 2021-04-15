import os

from citeminer.crawlers.collector import PaperCollector
from citeminer.utils import load_json

collector = PaperCollector()
config = load_json("./citeminer/configs/basic.json")
collector.init_from_config(config)
# collector.collect_metadata()
# collector.collect_pdfs()
collector.create_summaries()
