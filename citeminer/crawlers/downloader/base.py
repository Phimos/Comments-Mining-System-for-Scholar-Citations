from typing import Any

import requests


class BaseDownlaoder(object):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def simple_download(url: str, path: str) -> bool:
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
