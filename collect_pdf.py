from citeminer.crawlers.collector import PaperCollector
import json

collector = PaperCollector()
with open("./configs/basic.json") as infile:
    config = json.load(infile)
collector.init_from_config(config)


collector.collect_pdf_files()
