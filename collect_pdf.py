import json

from citeminer.crawlers.collector import PaperCollector

print("hello")
collector = PaperCollector()
with open("./citeminer/configs/test.json") as infile:
    config = json.load(infile)
collector.init_from_config(config)
collector.collect_metadata()
# collector.json_to_pdf("./result/metadata/Bingxuan Wang")
# print(config["authors"][0])
# out = collector.get_author_info(config["authors"][0])
# collector.scholar_crawler.pprint(out)
collector.collect_pdf_files()
