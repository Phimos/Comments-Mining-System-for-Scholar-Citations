import json
import logging
import os
import random
import re
import time
from functools import partial
from typing import Any, Dict, List, Optional, Union

import requests
from citeminer.crawlers.downloader import (
    AllInOneDownloader,
    DummyDownloader,
    HindawiDownloader,
    IEEEDownloader,
    SciHubDownloader,
    SimpleDownloader,
    WileyDownloader,
)
from citeminer.crawlers.scholar import ProxyGenerator, scholarly
from citeminer.crawlers.scihub import SciHub
from citeminer.pdfparser.parser import PDFParser
from citeminer.types import Author, Publication
from citeminer.utils import (
    apply_func,
    convert2txt,
    convert2txt_pdfx,
    count_pdf_files,
    count_txt_files,
    download_pdf,
    dump_json,
    fill_aminer_info,
    generate_summary,
    generate_tasks,
)
from citeminer.utils.markdown_writer import CitingDocument, CitingPublication


class PaperCollector(object):
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
        # TODO: use config to control year_low & year_high
        # TODO: not hard-code year_low & year_high in scholar code
        self.year_low = year_low
        self.year_high = year_high
        self.scholar_crawler = scholarly

        pg = ProxyGenerator()
        pg.SingleProxy(http="http://127.0.0.1:24000", https="http://127.0.0.1:24000")
        self.scholar_crawler.use_proxy(pg)

    # def _download_pdf(self, publication: Publication, save_dir: str) -> Optional[str]:
    #    ok = self.scihub_crawler.download(
    #        publication["pub_url"], save_dir, publication["bib"]["title"] + ".pdf"
    #    )
    #    return (
    #        os.path.join(save_dir, publication["bib"]["title"] + ".pdf")
    #        if ok is not None
    #        else None
    #    )

    @staticmethod
    def filename(name: str) -> str:
        newname = re.sub('[\/:*?"<>|]', "-", name)
        return newname

    def collect_metadata(self) -> None:
        os.makedirs(self.metadata_dir, exist_ok=True)
        for author in self.authors:
            author_info = self.collect_metadata_author_info(author)
            self.collect_metadata_publications(author_info)

    def collect_metadata_author_info(self, author):
        author_info = self.get_author_info(author)
        save_dir = os.path.join(self.metadata_dir, author_info["name"])
        dict_author_info = self.scholar_crawler.get_pprint(author_info)
        dump_json(dict_author_info, os.path.join(save_dir, "author_info.json"))
        return author_info

    def collect_metadata_publications(self, author_info) -> None:
        save_dir = os.path.join(self.metadata_dir, author_info["name"], "publications")
        os.makedirs(save_dir, exist_ok=True)
        for pub in author_info["publications"]:
            pub_dir = self.filename(pub["bib"]["title"])
            if os.path.exists(
                os.path.join(
                    save_dir, pub_dir, "%s.json" % self.filename(pub["bib"]["title"])
                )
            ):
                continue

            self.scholar_crawler.pprint(pub)

            if pub["num_citations"] > 0:
                cpubs = self.scholar_crawler.citedby(pub)
            else:
                cpubs = []
            os.makedirs(os.path.join(save_dir, pub_dir, "cited"), exist_ok=True)

            self.save_scholar_json(
                pub,
                os.path.join(
                    save_dir, pub_dir, "%s.json" % self.filename(pub["bib"]["title"])
                ),
            )

            for cpub in cpubs:
                self.scholar_crawler.pprint(cpub)
                # full_pub = self.scholar_crawler.fill(cpub)
                full_pub = cpub
                self.save_scholar_json(
                    full_pub,
                    os.path.join(
                        save_dir,
                        pub_dir,
                        "cited",
                        "%s.json" % self.filename(full_pub["bib"]["title"]),
                    ),
                )

    def save_scholar_json(self, info: Union[Author, Publication], path: str) -> None:
        # TODO: move the statement and delete this function
        if os.path.exists(path):
            print(path, "already exists")
            return
        else:
            dict_info = self.scholar_crawler.get_pprint(info)
            dump_json(dict_info, path)
            print(path, "saved.")

    def report(self) -> None:
        # TODO: move this function into utils module
        # TODO: add a new class to count number and report
        self.success = 0
        self.failed = 0
        self.undefined = 0

        def check_pdf(path):
            if os.path.isdir(path):
                for subpath in os.listdir(path):
                    check_pdf(os.path.join(path, subpath))
            else:
                with open(path) as infile:
                    info = json.load(infile)
                if "saved" in info.keys():
                    if info["saved"] == "success":
                        self.success += 1
                    else:
                        self.failed += 1
                else:
                    self.undefined += 1

        check_pdf(self.metadata_dir)
        print("[All document]:", self.success + self.failed + self.undefined)
        print("[Finished]:", self.success + self.failed)
        print("[Success]:", self.success)
        print("[Failed]:", self.failed)
        print(
            "[Finished Rate]: %.2f%%\t[Success Rate]: %.2f%%"
            % (
                100
                * (self.success + self.failed)
                / (self.success + self.failed + self.undefined),
                100 * (self.success) / (self.success + self.failed),
            )
        )

    def collect(self, config: Dict[str, Any]) -> None:
        # TODO: the function need to be deleted
        self.init_from_config(config)
        self.collect_metadata()

    def collect_pdfs(self) -> None:
        tasks = generate_tasks(self.metadata_dir, user_guide_info=self.authors)

        random.shuffle(tasks)

        # scihub_crawler = SciHub()
        # scihub_crawler.set_proxy("http://127.0.0.1:24000")

        downloader = AllInOneDownloader(
            [
                DummyDownloader(),
                SimpleDownloader(),
                IEEEDownloader(),
                HindawiDownloader(),
                WileyDownloader(),
                SciHubDownloader(),
            ]
        )

        apply_func(
            partial(
                download_pdf,
                metadata_dir=self.metadata_dir,
                pdf_dir=self.pdf_dir,
                # scihub_crawler=scihub_crawler,
                downloader=downloader,
            ),
            tasks,
        )

    def collect_aminer_info(self) -> None:
        tasks = generate_tasks(self.metadata_dir, user_guide_info=self.authors)
        apply_func(
            partial(
                fill_aminer_info,
                metadata_dir=self.metadata_dir,
                aminer_dir=self.aminer_dir,
            ),
            tasks,
        )

    def from_pdf_to_txt(self) -> None:
        """Convert PDF file into txt file (CPub-level Task)"""
        tasks = generate_tasks(
            self.metadata_dir, task_type="cpub", user_guide_info=self.authors
        )
        apply_func(
            partial(convert2txt, pdf_dir=self.pdf_dir, txt_dir=self.txt_dir),
            tasks,
            parallel=True,
            processes=2,
        )

    def create_summaries(self) -> None:
        tasks = generate_tasks(
            self.metadata_dir, task_type="pub", user_guide_info=self.authors
        )
        apply_func(
            partial(
                generate_summary,
                metadata_dir=self.metadata_dir,
                pdf_dir=self.pdf_dir,
                aminer_dir=self.aminer_dir,
                txt_dir=self.txt_dir,
                parser=PDFParser(),
            ),
            tasks,
        )

    def collect_pipeline(self) -> None:
        # TODO: make it a real function and test
        # collect_metadata_info
        # collect_pdf_files
        # fill_metadata_info
        # convert_pdf_2_txt
        # generate_summary
        pass

    def init_from_config(self, config: Dict[str, Any]) -> None:
        self.timeout = config.get("timeout", 20)
        result_dir = config.get("result_dir", "result")
        metadata_dir = config.get("metadata_dir", "metadata")
        pdf_dir = config.get("pdf_dir", "pdfs")
        txt_dir = config.get("txt_dir", "txts")
        aminer_dir = config.get("aminer_dir", "aminer")

        self.result_dir = os.path.join(".", result_dir)
        self.metadata_dir = os.path.join(self.result_dir, metadata_dir)
        self.pdf_dir = os.path.join(self.result_dir, pdf_dir)
        self.txt_dir = os.path.join(self.result_dir, txt_dir)
        self.aminer_dir = os.path.join(self.result_dir, aminer_dir)

        self.authors = config["authors"]

    def get_author_info(self, author: Dict[str, Any]) -> None:
        def contain_other_info(author: Dict[str, Any]) -> bool:
            for k in author.keys():
                if k in ["name", "publications"]:
                    continue
                else:
                    return True
            return False

        def check_same(result: Author, author: Dict[str, Any]) -> bool:
            for k in author.keys():
                if k in ["name", "publications"]:
                    continue
                elif result[k] != author[k]:
                    return False
                else:
                    pass
            return True

        assert "name" in author.keys()

        if contain_other_info(author):
            for result in self.scholar_crawler.search_author(author["name"]):
                if check_same(result, author):
                    return self.scholar_crawler.fill(result)

        else:
            result = next(self.scholar_crawler.search_author(author["name"]))
            result = self.scholar_crawler.fill(result)
            return result
