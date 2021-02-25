import requests
import pandas as pd
from bs4 import BeautifulSoup
from tenacity import retry
from tenacity import stop
from tenacity.wait import wait_random
from tenacity.stop import stop_after_attempt
from .base_proxy_crawler import BaseProxiesCrawler


class ProxyNova(BaseProxiesCrawler):
    """A Crawler of ProxyNova

    Proxy Nova is a website provide free proxy for various purposes.
    The url is https://www.proxynova.com

    Attributes:
        None
    """

    def __init__(self) -> None:
        super().__init__()
        # todo: set different anonymity level
        self.PROXY_NOVA_WEBSITE = (
            "https://www.proxynova.com/proxy-server-list/elite-proxies/"
        )

    @retry(
        wait=wait_random(1, 5),
        stop=stop_after_attempt(5),
        retry_error_callback=BaseProxiesCrawler.empty_proxies,
    )
    def get_proxies(self):
        response = requests.get(self.PROXY_NOVA_WEBSITE)

        self.logger.info(
            "Response code <%d> from website %s"
            % (response.status_code, self.PROXY_NOVA_WEBSITE)
        )

        soup = BeautifulSoup(response.text, "lxml")
        proxies_table = soup.select("table")[0].prettify()
        proxies_table = pd.read_html(proxies_table)[0]

        proxies_table = proxies_table[["Proxy IP", "Proxy Port"]]
        proxies_table = proxies_table.rename(
            columns={"Proxy IP": "ip address", "Proxy Port": "port"}
        )
        proxies_table["ip address"] = proxies_table["ip address"].str.extract(
            "(\d+\.\d+\.\d+\.\d+)", expand=False
        )
        proxies_table = proxies_table.dropna()
        proxies_table = proxies_table.drop_duplicates()
        return proxies_table


if __name__ == "__main__":
    pn = ProxyNova()
    out = pn.get_proxies()
    print(out)
