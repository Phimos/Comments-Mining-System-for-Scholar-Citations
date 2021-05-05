from typing import Any, List

from .base import BaseDownlaoder


class AllInOneDownloader(BaseDownlaoder):
    def __init__(self, downloaders: List[BaseDownlaoder]) -> None:
        super().__init__()
        self.downloaders = downloaders

    def download(self, url: str, path: str, **kwargs: Any) -> bool:
        for downloader in self.downloaders:
            if downloader.download(url, path, **kwargs):
                return True
        return False
