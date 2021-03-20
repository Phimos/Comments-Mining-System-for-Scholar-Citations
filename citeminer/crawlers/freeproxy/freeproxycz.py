import base64
import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop
from tenacity.stop import stop_after_attempt, stop_after_delay
from tenacity.wait import wait_random

from .base_proxy_crawler import BaseProxiesCrawler


class ProxyCZ(object):
    def __init__(self) -> None:
        super().__init__()
        self.PROXY_CZ_WEBSITE = "http://free-proxy.cz/en/proxylist/main/{}"

    def get_proxies(self, pages=5) -> pd.DataFrame:
        tables = []
        for i in range(1, pages + 1):
            tables.append(self.crawl_single_page(i))
        proxies_table = pd.concat(tables, ignore_index=True)
        proxies_table = proxies_table.drop_duplicates()
        return proxies_table

    @retry(
        wait=wait_random(1, 5),
        stop=(stop_after_delay(30) | stop_after_attempt(5)),
        retry_error_callback=BaseProxiesCrawler.empty_proxies,
    )
    def crawl_single_page(self, pagenum: int) -> pd.DataFrame:
        response = requests.get(self.PROXY_CZ_WEBSITE.format(pagenum))

        self.logger.info(
            "Response code <%d> from website %s"
            % (response.status_code, self.PROXY_CZ_WEBSITE.format(pagenum))
        )

        if response.status_code != 200:
            raise requests.exceptions.RequestException

        soup = BeautifulSoup(response.text, "lxml")
        proxies_table = soup.select("table")[1].prettify()
        proxies_table = pd.read_html(proxies_table)[0]

        proxies_table = proxies_table[["IP address", "Port"]]
        proxies_table = proxies_table.rename(
            columns={"IP address": "ip address", "Port": "port"}
        )
        proxies_table["ip address"] = proxies_table["ip address"].str.extract(
            'decode\("(.*)"\)'
        )
        proxies_table = proxies_table.dropna()
        proxies_table["ip address"] = proxies_table["ip address"].apply(
            lambda x: base64.b64decode(x).decode("ascii")
        )
        return proxies_table


if __name__ == "__main__":
    cz = ProxyCZ()
    result = cz.get_proxies()
    print(result)
