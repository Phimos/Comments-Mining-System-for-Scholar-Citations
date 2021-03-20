import pandas as pd
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random

from .base_proxy_crawler import BaseProxiesCrawler


class SSLProxies(BaseProxiesCrawler):
    def __init__(self) -> None:
        super().__init__()
        self.SSL_PROXIES_WEBSITE = "https://www.sslproxies.org"

    @retry(
        wait=wait_random(1, 5),
        stop=stop_after_attempt(5),
        retry_error_callback=BaseProxiesCrawler.empty_proxies,
    )
    def get_proxies(self) -> pd.DataFrame:
        response = requests.get(self.SSL_PROXIES_WEBSITE)
        self.logger.info(
            "Response code <%d> from website %s"
            % (response.status_code, self.SSL_PROXIES_WEBSITE)
        )
        soup = BeautifulSoup(response.text, "lxml")
        proxies_table = soup.select("table")[0].prettify()
        proxies_table = pd.read_html(proxies_table)[0]

        proxies_table = proxies_table.dropna()
        proxies_table = proxies_table[["IP Address", "Port"]]
        proxies_table = proxies_table.rename(
            columns={"IP Address": "ip address", "Port": "port"}
        )
        proxies_table["port"] = proxies_table["port"].astype(int).astype(str)
        proxies_table = proxies_table.drop_duplicates()
        return proxies_table


if __name__ == "__main__":
    out = SSLProxies().get_proxies()
    print(out)
