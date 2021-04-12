import json
from typing import Dict

import citeminer.crawlers
import citeminer.pdfparser
import citeminer.types
import citeminer.utils

debug = 1


def parse_config(config_path: str):
    assert config_path.endswith(".json")

    with open(config_path) as f:
        cfg: Dict = json.load(f)

    cfg.setdefault("metadata_save_dir", "./result/metadata")
    cfg.setdefault("pdf_save_dir", "./result/pdfs")

    cfg.setdefault("timeout", 10)
