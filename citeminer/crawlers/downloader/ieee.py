from typing import Any

import requests
from bs4 import BeautifulSoup

from .base import BaseDownlaoder


class IEEEDownloader(BaseDownlaoder):
    def __init__(self) -> None:
        super().__init__()

    def download(self, url: str, path: str, **kwargs: Any) -> bool:
        if "ieeexplore.ieee.org" not in url:
            return False

        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "lxml")
            real_url = soup.find("iframe").get("src")
        except:
            return False

        return self.simple_download(real_url, path)


class HindawiDownloader(BaseDownlaoder):
    def __init__(self) -> None:
        super().__init__()

    def download(self, url: str, path: str, **kwargs: Any) -> bool:
        if "www.hindawi.com" not in url:
            return False

        if not url.endswith(".pdf") and url.endswith("/"):
            real_url = url[:-1] + ".pdf"
            real_url = real_url.replace("www.hindawi.com", "downloads.hindawi.com")
        print(real_url)
        return self.simple_download(real_url, path)


class WileyDownloader(BaseDownlaoder):
    """
    Can't use
    """

    def __init__(self) -> None:
        super().__init__()

    def download(self, url: str, path: str, **kwargs: Any) -> bool:
        if "ietresearch.onlinelibrary.wiley.com" not in url:
            return False

        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "lxml")
            real_url = soup.find("iframe", attrs={"id": "pdf-iframe"}).get("src")
            real_url = "https://ietresearch.onlinelibrary.wiley.com" + real_url
        except:
            return False

        return self.simple_download(real_url, path)


if __name__ == "__main__":
    downloader = IEEEDownloader()
    downloader.download(
        "https://ieeexplore.ieee.org/iel7/8782710/8818473/09264716.pdf", "1.pdf"
    )
