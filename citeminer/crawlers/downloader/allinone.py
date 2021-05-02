from typing import List

from citeminer.crawlers.downloader import BaseDownlaoder


class AllInOneDownloader(BaseDownlaoder):
    def __init__(self, downloaders: List[BaseDownlaoder]) -> None:
        super().__init__()
        self.downloaders = downloaders

    def download(self, url: str, path: str) -> bool:
        for downloader in self.downloaders:
            if downloader.download(url, path):
                return True
        return False
