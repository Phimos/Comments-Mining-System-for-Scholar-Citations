from typing import Any

import requests


class BaseDownlaoder(object):
    """Base class of Downloader

    Downloader try download PDF document from web through the direct url or
    other information given like title or doi.

    Attributes:
        priority: An integer that can indicate the priority of the downloader.
                  The smaller the value, the higher the priority.
    """

    priority = 0

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def simple_download(url: str, path: str) -> bool:
        """Download PDF document using direct url

        Only when the URL corresponds to an online PDF document, the download
        will be successful.

        Args:
            url: A string representing the URL link of an online document.
            path: A string representing the local address where the document is
                  stored.

        Returns:
            A boolean variable indicating whether the download was successful.
        """
        if url == "":
            return False
        try:
            res = requests.get(url)
            if (
                "application/pdf" in res.headers["Content-Type"]
                or "application/octet-stream" in res.headers["Content-Type"]
                or "application/x-download" in res.headers["Content-Type"]
            ):
                with open(path, "wb") as f:
                    f.write(res.content)
                return True
            else:
                return False
        except:
            return False

    def download(self, url: str, path: str, **kwargs: Any) -> bool:
        return False
