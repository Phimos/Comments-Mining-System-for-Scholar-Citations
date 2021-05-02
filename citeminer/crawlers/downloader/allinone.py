class AllInOneDownloader(object):
    def __init__(self, downloaders) -> None:
        super().__init__()
        self.downloaders = downloaders

    def download(self, url: str, path: str) -> bool:
        for downloader in self.downloaders:
            if downloader.download(url, path):
                return True
        return False
