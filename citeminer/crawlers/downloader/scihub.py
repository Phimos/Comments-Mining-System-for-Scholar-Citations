# -*- coding: utf-8 -*-

"""
Sci-API Unofficial API
[Search|Download] research papers from [scholar.google.com|sci-hub.io].

@author zaytoun
"""
import argparse
import hashlib
import logging
import os
import random
import re
import time
from typing import Any, Optional

import requests
import urllib3
from bs4 import BeautifulSoup
from retrying import retry

from .base import BaseDownlaoder

# log config
logging.basicConfig()
logger = logging.getLogger("Sci-Hub")
logger.setLevel(logging.DEBUG)

#
urllib3.disable_warnings()

# constants
SCHOLARS_BASE_URL = "https://scholar.google.com/scholar"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0"
}


class SciHub(object):
    """
    SciHub class can search for papers on Google Scholars
    and fetch/download papers from sci-hub.io
    """

    def __init__(self):
        self.available_base_url_list = self._get_available_scihub_urls()
        self.base_url = self.available_base_url_list[0] + "/"

        self._proxy_works = False
        self._session = None
        self._new_session()

        self._retry_cnt = 0

    def _get_available_scihub_urls(self):
        """
        Finds available scihub urls via https://sci-hub.now.sh/
        """
        urls = []
        res = requests.get(
            "https://sci-hub.now.sh/",
            proxies={
                "http": "http://127.0.0.1:24000",
                "https": "http://127.0.0.1:24000",
            },
        )
        s = self._get_soup(res.content)
        for a in s.find_all("a", href=True):
            if "sci-hub." in a["href"]:
                urls.append(a["href"])
        return urls

    def set_proxy(self, proxy):
        """
        set proxy for session
        :param proxy_dict:
        :return:
        """
        if proxy:
            self._proxy_works = True
            self._session.proxies = {
                "http": proxy,
                "https": proxy,
            }
            self._new_session()

    def _new_session(self):
        proxies = {}
        if self._session:
            proxies = self._session.proxies
            self._close_session()
        self._session = requests.Session()
        self._session.headers.update(HEADERS)

        if self._proxy_works:
            self._session.proxies = proxies
        return self._session

    def _close_session(self):
        if self._session:
            self._session.close()

    def _change_base_url(self):
        if not self.available_base_url_list:
            raise Exception("Ran out of valid sci-hub urls")
        del self.available_base_url_list[0]
        self.base_url = self.available_base_url_list[0] + "/"
        logger.info("I'm changing to {}".format(self.available_base_url_list[0]))

    def search(self, query, limit=10, download=False):
        """
        Performs a query on scholar.google.com, and returns a dictionary
        of results in the form {'papers': ...}. Unfortunately, as of now,
        captchas can potentially prevent searches after a certain limit.
        """
        start = 0
        results = {"papers": []}

        while True:
            try:
                res = self._session.get(
                    SCHOLARS_BASE_URL, params={"q": query, "start": start}
                )
            except requests.exceptions.RequestException as e:
                results["err"] = (
                    "Failed to complete search with query %s (connection error)" % query
                )
                return results

            s = self._get_soup(res.content)
            papers = s.find_all("div", class_="gs_r")

            if not papers:
                if "CAPTCHA" in str(res.content):
                    results["err"] = (
                        "Failed to complete search with query %s (captcha)" % query
                    )
                return results

            for paper in papers:
                if not paper.find("table"):
                    source = None
                    pdf = paper.find("div", class_="gs_ggs gs_fl")
                    link = paper.find("h3", class_="gs_rt")

                    if pdf:
                        source = pdf.find("a")["href"]
                    elif link.find("a"):
                        source = link.find("a")["href"]
                    else:
                        continue

                    results["papers"].append({"name": link.text, "url": source})

                    if len(results["papers"]) >= limit:
                        return results

            start += 10

    #  @retry(wait_random_min=100, wait_random_max=1000, stop_max_attempt_number=10)
    def download(
        self, identifier, destination="", path=None
    ):  # todo: add session level retry
        """
        Downloads a paper from sci-hub given an indentifier (DOI, PMID, URL).
        Currently, this can potentially be blocked by a captcha if a certain
        limit has been reached.
        """
        print("scihub download:", identifier)

        data = self.fetch(identifier)

        if data and not "err" in data:
            self._retry_cnt = 0
            self._save(
                data["pdf"], os.path.join(destination, path if path else data["name"])
            )
            return True
        elif self._retry_cnt < 2:
            self._retry_cnt += 1
            self._new_session()
            return self.download(identifier, destination, path)
        else:
            return False

    def fetch(self, identifier):
        """
        Fetches the paper by first retrieving the direct link to the pdf.
        If the indentifier is a DOI, PMID, or URL pay-wall, then use Sci-Hub
        to access and download paper. Otherwise, just download paper directly.
        """

        try:
            url = self._get_direct_url(identifier)

            # verify=False is dangerous but sci-hub.io
            # requires intermediate certificates to verify
            # and requests doesn't know how to download them.
            # as a hacky fix, you can add them to your store
            # and verifying would work. will fix this later.
            res = self._session.get(url, verify=False)

            if res.headers["Content-Type"] != "application/pdf":
                self._change_base_url()
                logger.info(
                    "Failed to fetch pdf with identifier %s "
                    "(resolved url %s) due to captcha" % (identifier, url)
                )
                # raise CaptchaNeedException(
                #    "Failed to fetch pdf with identifier %s "
                #    "(resolved url %s) due to captcha" % (identifier, url)
                # )
                return {
                    "err": "Failed to fetch pdf with identifier %s (resolved url %s) due to captcha"
                    % (identifier, url)
                }
            else:
                return {
                    "pdf": res.content,
                    "url": url,
                    "name": self._generate_name(res),
                }

        except requests.exceptions.ConnectionError:
            logger.info(
                "Cannot access {}, changing url".format(self.available_base_url_list[0])
            )
            self._change_base_url()

        except requests.exceptions.RequestException as e:
            logger.info(
                "Failed to fetch pdf with identifier %s (resolved url %s) due to request exception."
                % (identifier, url)
            )
            return {
                "err": "Failed to fetch pdf with identifier %s (resolved url %s) due to request exception."
                % (identifier, url)
            }

    def _get_direct_url(self, identifier):
        """
        Finds the direct source url for a given identifier.
        """
        id_type = self._classify(identifier)

        return (
            identifier
            if id_type == "url-direct"
            else self._search_direct_url(identifier)
        )

    def _search_direct_url(self, identifier):
        """
        Sci-Hub embeds papers in an iframe. This function finds the actual
        source url which looks something like https://moscow.sci-hub.io/.../....pdf.
        """
        res = self._session.get(self.base_url + identifier, verify=False)
        s = self._get_soup(res.content)
        iframe = s.find("iframe")
        if iframe:
            return (
                iframe.get("src")
                if not iframe.get("src").startswith("//")
                else "http:" + iframe.get("src")
            )

    def _classify(self, identifier):
        """
        Classify the type of identifier:
        url-direct - openly accessible paper
        url-non-direct - pay-walled paper
        pmid - PubMed ID
        doi - digital object identifier
        """
        if identifier.startswith("http") or identifier.startswith("https"):
            if identifier.endswith("pdf"):
                return "url-direct"
            else:
                return "url-non-direct"
        elif identifier.isdigit():
            return "pmid"
        else:
            return "doi"

    def _save(self, data, path):
        """
        Save a file give data and a path.
        """
        try:
            with open(path, "wb") as f:
                f.write(data)
        except:
            pass

    def _get_soup(self, html):
        """
        Return html soup.
        """
        return BeautifulSoup(html, "html.parser")

    def _generate_name(self, res):
        """
        Generate unique filename for paper. Returns a name by calcuating
        md5 hash of file contents, then appending the last 20 characters
        of the url which typically provides a good paper identifier.
        """
        name = res.url.split("/")[-1]
        name = re.sub("#view=(.+)", "", name)
        pdf_hash = hashlib.md5(res.content).hexdigest()
        return "%s-%s" % (pdf_hash, name[-20:])


class CaptchaNeedException(Exception):
    pass


class SciHubDownloader(BaseDownlaoder):
    def __init__(self) -> None:
        super().__init__()

    def download(
        self, url: str, path: str, title: str, doi: Optional[str] = None, **kwargs: Any
    ) -> bool:
        try:
            html = requests.post(
                random.choice(
                    [
                        "https://sci-hub.se/",
                        "https://sci-hub.st/",
                        "https://sci-hub.do/",
                    ]
                ),
                {"request": title},
            )
            print(html)
            html.encoding = html.apparent_encoding
            soup = BeautifulSoup(html.text, "lxml")
            real_url = soup.find("iframe").get("src")
            real_url = re.sub("#view=(.+)", "", real_url)
            if not real_url.startswith("https:"):
                real_url = "https:" + real_url
            print(real_url)
        except:
            return False

        time.sleep(random.uniform(5, 20))

        return self.simple_download(real_url, path)


def main():
    sh = SciHub()

    parser = argparse.ArgumentParser(
        description="SciHub - To remove all barriers in the way of science."
    )
    parser.add_argument(
        "-d",
        "--download",
        metavar="(DOI|PMID|URL)",
        help="tries to find and download the paper",
        type=str,
    )
    parser.add_argument(
        "-f",
        "--file",
        metavar="path",
        help="pass file with list of identifiers and download each",
        type=str,
    )
    parser.add_argument(
        "-s", "--search", metavar="query", help="search Google Scholars", type=str
    )
    parser.add_argument(
        "-sd",
        "--search_download",
        metavar="query",
        help="search Google Scholars and download if possible",
        type=str,
    )
    parser.add_argument(
        "-l",
        "--limit",
        metavar="N",
        help="the number of search results to limit to",
        default=10,
        type=int,
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="path",
        help="directory to store papers",
        default="",
        type=str,
    )
    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "-p",
        "--proxy",
        help="via proxy format like socks5://user:pass@host:port",
        action="store",
        type=str,
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    if args.proxy:
        sh.set_proxy(args.proxy)

    if args.download:
        result = sh.download(args.download, args.output)
        if "err" in result:
            logger.debug("%s", result["err"])
        else:
            logger.debug(
                "Successfully downloaded file with identifier %s", args.download
            )
    elif args.search:
        results = sh.search(args.search, args.limit)
        if "err" in results:
            logger.debug("%s", results["err"])
        else:
            logger.debug("Successfully completed search with query %s", args.search)
        print(results)
    elif args.search_download:
        results = sh.search(args.search_download, args.limit)
        if "err" in results:
            logger.debug("%s", results["err"])
        else:
            logger.debug(
                "Successfully completed search with query %s", args.search_download
            )
            for paper in results["papers"]:
                result = sh.download(paper["url"], args.output)
                if "err" in result:
                    logger.debug("%s", result["err"])
                else:
                    logger.debug(
                        "Successfully downloaded file with identifier %s", paper["url"]
                    )
    elif args.file:
        with open(args.file, "r") as f:
            identifiers = f.read().splitlines()
            for identifier in identifiers:
                result = sh.download(identifier, args.output)
                if "err" in result:
                    logger.debug("%s", result["err"])
                else:
                    logger.debug(
                        "Successfully downloaded file with identifier %s", identifier
                    )


if __name__ == "__main__":
    main()
