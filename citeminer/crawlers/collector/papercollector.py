import json
import logging
import os
import random
import re
import time
from typing import Any, Dict, List, Optional, Union

import requests
from citeminer.crawlers.scholar import ProxyGenerator, scholarly
from citeminer.crawlers.scihub import *
from citeminer.types import Author, Publication
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
        self.year_low = year_low
        self.year_high = year_high
        self.scholar_crawler = scholarly
        self.scihub_crawler = SciHub()
        pg = ProxyGenerator()
        pg.SingleProxy(http="http://127.0.0.1:24000", https="http://127.0.0.1:24000")
        self.scholar_crawler.use_proxy(pg)
        self.scihub_crawler.set_proxy("http://127.0.0.1:24000")

    def collect_by_author(self, name: str) -> None:
        save_dir = os.path.join(self.result_dir, name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        author = next(self.scholar_crawler.search_author(name))
        scholarly.pprint(author)
        author = self.scholar_crawler.fill(author)
        for pub in author["publications"]:
            self.collect_by_publication(pub, name)

    def collect_by_publication(
        self, publication: Publication, author: str = "John Doe"
    ) -> None:
        save_dir = os.path.join(self.result_dir, author, publication["bib"]["title"])
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        cd = CitingDocument(
            publication, document_path=os.path.join(save_dir, "summary.md")
        )
        cnt = 0
        cpubs = self.scholar_crawler.citedby(publication)
        for i, val in enumerate(cpubs):
            pub = self.scholar_crawler.fill(val)

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

    def _download_pdf(self, publication: Publication, save_dir: str) -> Optional[str]:
        ok = self.scihub_crawler.download(
            publication["pub_url"], save_dir, publication["bib"]["title"] + ".pdf"
        )
        return (
            os.path.join(save_dir, publication["bib"]["title"] + ".pdf")
            if ok is not None
            else None
        )

    @staticmethod
    def filename(name: str) -> str:
        newname = re.sub('[\/:*?"<>|]', "-", name)
        return newname

    def collect_metadata(self):
        os.makedirs(self.metadata_save_dir, exist_ok=True)
        for author in self.authors:
            author_info = self.collect_metadata_author_info(author)
            self.collect_metadata_publications(author_info)

    def collect_metadata_author_info(self, author):
        author_info = next(self.scholar_crawler.search_author(author["name"]))
        author_info = self.scholar_crawler.fill(author_info)
        save_dir = os.path.join(self.metadata_save_dir, author_info["name"])
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, "author_info.json"), "w") as outfile:
            dict_author_info = self.scholar_crawler.get_pprint(author_info)
            json.dump(
                dict_author_info,
                outfile,
                sort_keys=True,
                indent=4,
                separators=(",", ":"),
            )
        return author_info

    def save_scholar_json(self, info: Union[Author, Publication], path: str):
        if os.path.exists(path):
            print(path, "already exists")
            return
        else:
            pardir, filename = os.path.split(path)
            os.makedirs(pardir, exist_ok=True)
            dict_info = self.scholar_crawler.get_pprint(info)
            with open(path, "w") as outfile:
                json.dump(
                    dict_info,
                    outfile,
                    sort_keys=True,
                    indent=4,
                    separators=(",", ":"),
                )
            print(path, "saved.")

    def collect_metadata_publications(self, author_info) -> None:
        save_dir = os.path.join(
            self.metadata_save_dir, author_info["name"], "publications"
        )
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

    def collect_pdf_files(self) -> None:
        self.json_to_pdf(self.metadata_save_dir)

    def json_to_pdf(self, path: str) -> None:

        if os.path.isdir(path):
            for subpath in os.listdir(path):
                self.json_to_pdf(os.path.join(path, subpath))

        elif os.path.isfile(path):
            with open(path) as infile:
                info = json.load(infile)

            if "pub_url" in info.keys():
                if "saved" in info.keys():
                    if info["saved"] == "success":
                        print("[&success]:", info["bib"]["title"])
                        return
                    else:
                        print("[&failed]:", info["bib"]["title"])
                        pass

                pdf_path = path
                pdf_path = pdf_path.replace(self.metadata_save_dir, self.pdf_save_dir)
                pdf_path = pdf_path.replace(".json", ".pdf")

                pardir, _ = os.path.split(pdf_path)
                os.makedirs(pardir, exist_ok=True)

                if "eprint_url" in info.keys():
                    ok = self.simple_download(info["eprint_url"], path=pdf_path)
                    if not ok:
                        ok = self.scihub_crawler.download(
                            info["pub_url"], path=pdf_path
                        )
                else:
                    ok = self.scihub_crawler.download(info["pub_url"], path=pdf_path)
                if ok:
                    info["saved"] = "success"
                    print("[success]:", info["bib"]["title"])
                else:
                    info["saved"] = "failed"
                    print("[failed]:", info["bib"]["title"])

                with open(path, "w") as outfile:
                    json.dump(
                        info,
                        outfile,
                        sort_keys=True,
                        indent=4,
                        separators=(",", ":"),
                    )

                if random.random() < 0.05:  # long sleep
                    # time.sleep(random.uniform(60, 300))
                    pass
                else:  # short sleep
                    time.sleep(random.uniform(1, 2))

    def simple_download(self, url, path):
        print("Simple download:", url)
        try:
            res = requests.get(url)
            if (
                "application/pdf" in res.headers["Content-Type"]
                or "application/octet-stream" in res.headers["Content-Type"]
                or "application/x-download" in res.headers["Content-Type"]
            ):
                try:
                    with open(path, "wb") as f:
                        f.write(res.content)
                except:
                    pass
                return True
            else:
                return False
        except:
            return False

    def webdriver_download(self, url, path):
        print("Webdriver download:", url)

    def report(self) -> None:
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

        check_pdf(self.metadata_save_dir)
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
        self.init_from_config(config)
        self.collect_metadata()
        self.collect_pdf_files()
        pass

    def init_from_config(self, config: Dict[str, Any]) -> None:
        self.timeout = config["timeout"]
        self.metadata_save_dir = config["metadata_save_dir"]
        self.pdf_save_dir = config["pdf_save_dir"]
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
