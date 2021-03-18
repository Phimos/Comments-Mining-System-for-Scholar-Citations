from crawlers import *
from utils.markdown_writer import CitingDocument, CitingPublication
from typing import Optional, List
from crawlers.scholarly import ProxyGenerator
import logging
import json
import os


class PaperCollecter(object):
    def __init__(
        self,
        author: Optional[str] = None,
        publications: Optional[List[str]] = None,
        year_low: Optional[int] = 2020,
        year_high: Optional[int] = 2020,
        result_dir: str = "./result",
    ) -> None:
        super().__init__()
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)
        self.result_dir = result_dir
        self.author = author
        self.publictions = publications
        self.year_low = year_low
        self.year_high = year_high
        self.scholar_crawler = scholarly
        self.scihub_crawler = SciHub()
        pg = ProxyGenerator()
        pg.SingleProxy(http="http://127.0.0.1:24000", https="http://127.0.0.1:24000")
        self.scholar_crawler.use_proxy(pg)

    def collect_by_author(self, name: str):
        save_dir = os.path.join(self.result_dir, name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        author = next(self.scholar_crawler.search_author(name))
        scholarly.pprint(author)
        author = self.scholar_crawler.fill(author)
        for pub in author["publications"]:
            self.collect_by_publication(pub, name)
        pass

    def collect_by_publication(
        self, publication: Publication, author: str = "John Doe"
    ):
        save_dir = os.path.join(self.result_dir, author, publication["bib"]["title"])
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        cd = CitingDocument(
            publication, document_path=os.path.join(save_dir, "summary.md")
        )
        cnt = 0
        citing_publictions = self.scholar_crawler.citedby(publication)
        for i, val in enumerate(citing_publictions):
            pub = self.scholar_crawler.fill(val)
            self.scholar_crawler.pprint(pub)

            tmp = self._download_pdf(pub, save_dir)
            if tmp is None:
                self.scihub_crawler = SciHub()  # reset
                print("new type reset!")
            else:
                pub["pub_url"] = tmp
            cd.add_publication(pub)
            self.scholar_crawler.pprint(pub)
            cnt = cnt + 1
            if cnt >= 10:
                break
        cd.save()

    def _download_pdf(self, publication: Publication, save_dir: str):
        ok = self.scihub_crawler.download(
            publication["pub_url"], save_dir, publication["bib"]["title"] + ".pdf"
        )
        return (
            os.path.join(save_dir, publication["bib"]["title"] + ".pdf")
            if ok is not None
            else None
        )

    def collect_metadata(self):
        os.makedirs(self.metadata_save_dir, exist_ok=True)
        for author in self.authors:
            author_info = self.collect_metadata_author_info(author)
            self.collect_metadata_publications(author_info)

    def collect_metadata_author_info(self, author):
        save_dir = os.path.join(self.metadata_save_dir, author["name"])
        os.makedirs(save_dir, exist_ok=True)
        author_info = next(self.scholar_crawler.search_author(author["name"]))
        author_info = self.scholar_crawler.fill(author_info)
        with open(os.path.join(save_dir, "author_info.json"), "w") as outfile:
            dict_author_info = dict(author_info).copy()
            dict_author_info.pop("filled")
            dict_author_info.pop("source")
            print(dict_author_info)
            json.dump(dict_author_info, outfile)
        return author_info

    def collect_metadata_publications(self, author):
        pass

    def collect_pdf_files(self):
        pass

    def collect(self, config):
        self.init_from_config(config)
        self.collect_metadata()
        self.collect_pdf_files()
        pass

    def init_from_config(self, config):
        self.timeout = config["timeout"]
        self.metadata_save_dir = config["metadata_save_dir"]
        self.pdf_save_dir = config["pdf_save_dir"]
        self.authors = config["authors"]


"""
# log config
logging.basicConfig()
logger = logging.getLogger("Sci-Hub")
logger.setLevel(logging.DEBUG)

sh = SciHub()
sh.set_proxy("http://127.0.0.1:9999")
for pub in publications:
    result = sh.download(pub["link"], path=pub["title"] + ".pdf")
    if "err" in result:
        logger.debug("%s", result["err"])
    else:
        logger.debug("Successfully downloaded file with identifier %s", pub["title"])
"""


pc = PaperCollecter()

pc.collect_by_author("Zhouchen Lin")
exit(0)

with open("./configs/basic.json") as infile:
    config = json.load(infile)
print(config)
pc.init_from_config(config)
pc.collect_metadata()
