import os

from selenium import webdriver
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
        """
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless') #浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) >AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.57')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--hide-scrollbars') #隐藏滚动条, 应对一些特殊页面
        self.chrome_options.add_argument('blink-settings=imagesEnabled=false') #不加载图片, 提升速度
        #实现规避操作
        option = ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        browser = webdriver.Chrome(chrome_options=chrome_options, options=option)
        #browser = webdriver.Chrome()
        script = '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                '''
        browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})
        """
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
