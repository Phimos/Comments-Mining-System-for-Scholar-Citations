import requests
import selenium


class SimpleDownloader(object):
    def __init__(self) -> None:
        super().__init__()

    def download(self, url: str, path: str) -> bool:
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
