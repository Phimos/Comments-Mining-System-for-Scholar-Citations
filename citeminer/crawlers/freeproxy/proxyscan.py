from typing import List

import pandas as pd
import requests
from tenacity import retry, stop
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random

from .base_proxy_crawler import BaseProxiesCrawler


class ProxyScan(BaseProxiesCrawler):
    def __init__(self) -> None:
        super().__init__()
        self.PROXY_SCAN_DOWNLOAD = "https://www.proxyscan.io/download?type={}"

    def _construct_dataframe(self, proxies: List[str]) -> pd.DataFrame:
        proxies = [proxy.split(":") for proxy in proxies]
        return pd.DataFrame(proxies, columns=["ip address", "port"])

    @retry(
        wait=wait_random(1, 5),
        stop=stop_after_attempt(5),
        retry_error_callback=BaseProxiesCrawler.empty_proxies,
    )
    def get_http_proxies(self) -> pd.DataFrame:
        response = requests.get(self.PROXY_SCAN_DOWNLOAD.format("http"))
        self.logger.info(
            "Response code <%d> from website %s"
            % (response.status_code, self.PROXY_SCAN_DOWNLOAD.format("http"))
        )
        return self._construct_dataframe(response.text.split("\n"))

    @retry(
        wait=wait_random(1, 5),
        stop=stop_after_attempt(5),
        retry_error_callback=BaseProxiesCrawler.empty_proxies,
    )
    def get_https_proxies(self) -> pd.DataFrame:
        response = requests.get(self.PROXY_SCAN_DOWNLOAD.format("https"))
        self.logger.info(
            "Response code <%d> from website %s"
            % (response.status_code, self.PROXY_SCAN_DOWNLOAD.format("https"))
        )
        return self._construct_dataframe(response.text.split("\n"))

    @retry(
        wait=wait_random(1, 5),
        stop=stop_after_attempt(5),
        retry_error_callback=BaseProxiesCrawler.empty_proxies,
    )
    def get_socks4_proxies(self) -> pd.DataFrame:
        response = requests.get(self.PROXY_SCAN_DOWNLOAD.format("socks4"))
        self.logger.info(
            "Response code <%d> from website %s"
            % (response.status_code, self.PROXY_SCAN_DOWNLOAD.format("socks4"))
        )
        return self._construct_dataframe(response.text.split("\n"))

    @retry(
        wait=wait_random(1, 5),
        stop=stop_after_attempt(5),
        retry_error_callback=BaseProxiesCrawler.empty_proxies,
    )
    def get_socks5_proxies(self) -> pd.DataFrame:
        response = requests.get(self.PROXY_SCAN_DOWNLOAD.format("socks5"))
        self.logger.info(
            "Response code <%d> from website %s"
            % (response.status_code, self.PROXY_SCAN_DOWNLOAD.format("socks5"))
        )
        return self._construct_dataframe(response.text.split("\n"))

    def get_proxies(self) -> pd.DataFrame:
        http_proxies = self.get_http_proxies()
        https_proxies = self.get_https_proxies()
        socks4_proxies = self.get_socks4_proxies()
        socks5_proxies = self.get_socks5_proxies()
        proxies = pd.concat(
            [http_proxies, https_proxies, socks4_proxies, socks5_proxies],
            ignore_index=True,
        )
        proxies = proxies.drop_duplicates(ignore_index=True)
        return proxies


if __name__ == "__main__":
    proxy_scrape = ProxyScan()
    ret = proxy_scrape.get_proxies()
    print(ret)
