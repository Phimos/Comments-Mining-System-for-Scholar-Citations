from selenium import webdriver
import os

from selenium.webdriver.chrome.options import Options

chromedriver = (
    "/home/ganyunchong/Comments-Mining-System-for-Scholar-Citations/chromedriver"
)
os.environ["webdriver.chrome.driver"] = chromedriver


class ChromePDFDownloader(object):
    def __init__(self, binary_location="/usr/bin/chrome-linux/chrome") -> None:
        # basic config
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--no-gpu")
        self.chrome_options.add_argument("--disable-setuid-sandbox")
        self.chrome_options.add_argument("--single-process")
        self.chrome_options.add_argument("--window-size=1920,1080")

        # chrome binary location set
        self.chrome_options.binary_location = binary_location
        super().__init__()

    def download(self, url, path):
        browser = webdriver.Chrome(chromedriver, options=self.chrome_options)
        browser.get("https://baidu.com/")
        browser.save_screenshot("no_windows.png")
        print(browser.page_source)


if __name__ == "__main__":
    downloader = ChromePDFDownloader()
    downloader.download(None, None)
