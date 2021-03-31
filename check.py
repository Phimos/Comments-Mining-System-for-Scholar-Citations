import json

import tableprint as tp

from citeminer.crawlers.collector import PaperCollector
from citeminer.utils.analysis import collect_failed_data

collector = PaperCollector()
with open("./citeminer/configs/basic.json") as infile:
    config = json.load(infile)
collector.init_from_config(config)

# collector.report()


collect_failed_data(config["metadata_save_dir"])
