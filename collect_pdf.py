import json

from citeminer.crawlers.collector import PaperCollector

print("hello")
collector = PaperCollector()
with open("./citeminer/configs/test.json") as infile:
    config = json.load(infile)
collector.init_from_config(config)
collector.collect_metadata()
# out = collector.get_author_info(config["authors"][0])
# collector.scholar_crawler.pprint(out)
collector.collect_pdfs()
