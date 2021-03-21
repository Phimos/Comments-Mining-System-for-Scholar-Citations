import json

from citeminer.crawlers.collector import PaperCollector

collector = PaperCollector()
with open("./citeminer/configs/basic.json") as infile:
    config = json.load(infile)
collector.init_from_config(config)


collector.collect_pdf_files()
