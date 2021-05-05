from typing import Any

import requests

from .base import BaseDownlaoder


class SimpleDownloader(BaseDownlaoder):
    def __init__(self) -> None:
        super().__init__()

    def download(self, url: str, path: str, **kwargs: Any) -> bool:
        return self.simple_download(url, path)
