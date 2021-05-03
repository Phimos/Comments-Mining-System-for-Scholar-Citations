import requests
from bs4 import BeautifulSoup


class IEEEDownloader(object):
    def __init__(self) -> None:
        super().__init__()

    def download(self, url: str, path: str) -> bool:
        if "ieeexplore.ieee.org" not in url:
            return False

        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "lxml")
            real_url = soup.find("iframe").get("src")

            res = requests.get(real_url)
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


if __name__ == "__main__":
    downloader = IEEEDownloader()
    downloader.download(
        "https://ieeexplore.ieee.org/iel7/8782710/8818473/09264716.pdf", "1.pdf"
    )
