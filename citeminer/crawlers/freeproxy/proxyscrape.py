from typing import List

import pandas as pd
import requests
from tenacity import retry
from tenacity import stop
from tenacity.wait import wait_random
from tenacity.stop import stop_after_attempt
from .base_proxy_crawler import BaseProxiesCrawler


class ProxyScrape(BaseProxiesCrawler):
    def __init__(self) -> None:
        super().__init__()
        self.PROXY_SCRAPE_DOWNLOAD = (
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol={}"
        )

    def _construct_dataframe(self, proxies: List[str]) -> pd.DataFrame:
        proxies = [proxy.split(":") for proxy in proxies]
        return pd.DataFrame(proxies, columns=["ip address", "port"])

    @retry(
        wait=wait_random(1, 5),
        stop=stop_after_attempt(5),
        retry_error_callback=BaseProxiesCrawler.empty_proxies,
    )
    def get_http_proxies(self) -> pd.DataFrame:
        response = requests.get(self.PROXY_SCRAPE_DOWNLOAD.format("http"))
        self.logger.info(
            "Response code <%d> from website %s"
            % (response.status_code, self.PROXY_SCRAPE_DOWNLOAD.format("http"))
        )
        return self._construct_dataframe(response.text.split("\r\n"))

    @retry(
        wait=wait_random(1, 5),
        stop=stop_after_attempt(5),
        retry_error_callback=BaseProxiesCrawler.empty_proxies,
    )
    def get_socks4_proxies(self) -> pd.DataFrame:
        response = requests.get(self.PROXY_SCRAPE_DOWNLOAD.format("socks4"))
        self.logger.info(
            "Response code <%d> from website %s"
            % (response.status_code, self.PROXY_SCRAPE_DOWNLOAD.format("socks4"))
        )
        return self._construct_dataframe(response.text.split("\r\n"))

    @retry(
        wait=wait_random(1, 5),
        stop=stop_after_attempt(5),
        retry_error_callback=BaseProxiesCrawler.empty_proxies,
    )
    def get_socks5_proxies(self) -> pd.DataFrame:
        response = requests.get(self.PROXY_SCRAPE_DOWNLOAD.format("socks5"))
        self.logger.info(
            "Response code <%d> from website %s"
            % (response.status_code, self.PROXY_SCRAPE_DOWNLOAD.format("socks5"))
        )
        return self._construct_dataframe(response.text.split("\r\n"))

    def get_proxies(self) -> pd.DataFrame:
        http_proxies = self.get_http_proxies()
        socks4_proxies = self.get_socks4_proxies()
        socks5_proxies = self.get_socks5_proxies()
        proxies = pd.concat(
            [http_proxies, socks4_proxies, socks5_proxies], ignore_index=True
        )
        proxies = proxies.drop_duplicates(ignore_index=True)
        return proxies


if __name__ == "__main__":
    proxy_scrape = ProxyScrape()
    ret = proxy_scrape.get_proxies()
    print(ret)
