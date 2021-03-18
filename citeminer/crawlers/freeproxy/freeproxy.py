import pandas as pd
import os
import requests
from typing import Dict
from tqdm import tqdm
import random

from .proxyscan import ProxyScan
from .proxyscrape import ProxyScrape
from .freeproxycz import ProxyCZ
from .sslproxies import SSLProxies
from .proxynova import ProxyNova


class FreeProxyPool(object):
    def __init__(
        self,
        refresh: bool = False,
        download: bool = False,
        save: bool = True,
        ip_save_path: str = "./ips.csv",
    ) -> None:
        super().__init__()
        # self.TEST_URL = "http://assets.nflxext.com"

        self.ip_save_path = ip_save_path
        self.TEST_URL = "https://scholar.google.com/scholar?q=covid"
        self.HTTP_PROXY = "http://{}:{}"
        self.HTTPS_PROXY = "https://{}:{}"
        self.TIMEOUT = 5
        self.proxies = self.get_proxies(refresh, download, save, ip_save_path)

        self.proxies_gen = list(
            self.proxies.apply(lambda x: self.format_proxy(*x), axis=1, raw=True)
        )
        random.shuffle(self.proxies_gen)
        self.proxies_gen = iter(self.proxies_gen)

    def __call__(self) -> str:
        return self.next_proxy()["http"]

    def get_proxies(
        self, refresh: bool, download: bool, save: bool, ip_save_path: str
    ) -> pd.DataFrame:
        """Crawl proxies

        Args:
            refresh (bool):
            download (bool):
            save (bool):
            ip_save_path (str): 
        
        Returns:
            proxies (pandas.DataFrame): contains the proxies we get.
            Each row is represented as a proxy, an ip address and a port.
        """
        if download:
            # proxies_crawlers = [ProxyScan(), ProxyScrape(), SSLProxies(), ProxyNova()]
            proxies_crawlers = [ProxyNova()]
            proxies_tables = []
            for crawler in proxies_crawlers:
                proxies_tables.append(crawler.get_proxies())
            proxies = pd.concat(proxies_tables, ignore_index=True)
            if os.path.exists(ip_save_path):
                if not refresh:
                    old_proxies = pd.read_csv(ip_save_path)
                    proxies = pd.concat([proxies, old_proxies], ignore_index=True)
            proxies = proxies.dropna()
            proxies = proxies.drop_duplicates(ignore_index=True)
            proxies["port"] = proxies["port"].astype(int).astype(str)
            if save:
                proxies.to_csv(ip_save_path, index=False)
            return proxies
        else:
            if os.path.exists(ip_save_path):
                proxies = pd.read_csv(ip_save_path)
                proxies = proxies.dropna()
                proxies = proxies.drop_duplicates(ignore_index=True)
                proxies["port"] = proxies["port"].astype(int).astype(str)
                return proxies
            else:
                raise ValueError

    def format_proxy(self, ip: str, port: str) -> Dict[str, str]:
        return {
            "http": self.HTTP_PROXY.format(ip, port),
            "https": self.HTTPS_PROXY.format(ip, port),
        }

    def next_proxy(self) -> Dict[str, str]:
        proxy = next(self.proxies_gen)
        while not self.verify_proxy(proxy):
            proxy = next(self.proxies_gen)
        return proxy

    def update_all(self) -> str:
        formatted_proxies = self.proxies.apply(
            lambda x: self.format_proxy(*x), axis=1, raw=True
        )
        valid_indices = []
        print("total:", len(formatted_proxies))
        for proxy in tqdm(formatted_proxies):
            valid_indices.append(self.verify_proxy(proxy))
        self.proxies = self.proxies[valid_indices]
        print("checked:", len(self.proxies))
        pass

    def verify_proxy(self, proxy) -> bool:
        print("verify proxy:", proxy)
        with requests.Session() as session:
            session.proxies = proxy
            try:
                response = session.get(self.TEST_URL, timeout=self.TIMEOUT)
                if response.status_code == 200:
                    return True
            except:
                pass
            return False


if __name__ == "__main__":
    fp = FreeProxyPool()
    fp.verify_proxy({"http": "http://191.101.39.29:80", "https": None})
