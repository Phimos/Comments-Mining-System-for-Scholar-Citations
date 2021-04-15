import os

from citeminer.crawlers.collector import PaperCollector
from citeminer.utils import load_json

collector = PaperCollector()
config = load_json("./citeminer/configs/test.json")
collector.init_from_config(config)
collector.collect_metadata()

collector.collect_aminer_info()

collector.collect_pdfs()

collector.from_pdf_to_txt()

collector.create_summaries()
