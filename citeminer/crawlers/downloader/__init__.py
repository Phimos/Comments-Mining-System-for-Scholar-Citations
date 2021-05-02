from typing import AbstractSet

from .scihub import SciHub
from .simple import SimpleDownloader


class BaseDownlaoder(object):
    def __init__(self) -> None:
        super().__init__()

    def download(self, url: str, path: str) -> bool:
        return False


__all__ = ["SciHub", "SimpleDownloader"]
