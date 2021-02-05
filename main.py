from crawlers import *
from utils.markdown_writer import CitingPublication
from typing import Optional, List
from crawlers.freeproxy.freeproxy import FreeProxyPool
import logging
import os


class PaperCollecter(object):
    def __init__(
        self,
        author: Optional[str] = None,
        publications: Optional[List[str]] = None,
        year_low: Optional[int] = 2020,
        year_high: Optional[int] = 2020,
        result_dir: str = "./result",
        http_proxy: Optional[str] = "http://127.0.0.1:9999",
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

    def collect(self):
        pass

    def collect_by_author(self, name: str):
        save_dir = os.path.join(self.result_dir, name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        author = next(self.scholar_crawler.search_author(name))
        scholarly.pprint(author)
        author = self.scholar_crawler.fill(author)
        for pub in author["publications"]:
            # scholarly.pprint(scholarly.fill(pub))
            self.collect_by_publication(pub, name)
            break

        pass

    def collect_by_publication(
        self, publication: Publication, author: str = "John Doe"
    ):
        save_dir = os.path.join(self.result_dir, author, publication["bib"]["title"])
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        for i, val in enumerate(self.scholar_crawler.citedby(publication)):
            scholarly.pprint(val)
            # with open("test.md", "w") as f:
            #    f.write(CitingPublication(publication=scholarly.fill(val)).stream)

    def _collect_citation_info():
        pass

    def _collect_pdf_files(self):
        pass


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

