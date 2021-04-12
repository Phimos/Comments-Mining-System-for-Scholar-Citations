import json
import os
import random
import re
import time
from functools import wraps
from pprint import pprint
from typing import Any, Dict, List, Optional, Union

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

timeout = 20
chromedriver = (
    "/home/ganyunchong/Comments-Mining-System-for-Scholar-Citations/chromedriver"
)
os.environ["webdriver.chrome.driver"] = chromedriver


class Author(object):
    def __init__(
        self, name: str, email: Optional[str] = None, rank: Optional[int] = None
    ) -> None:
        super().__init__()
        self.name = name
        self.email = email
        self.rank = rank

    def to_json(self, json_path: str) -> None:
        pass

    def dict(self) -> Dict[str, Any]:
        author = dict()
        author["name"] = self.name
        if self.email is not None:
            author["email"] = self.email
        return author


class Publication(object):
    def __init__(
        self,
        title: str,
        authors: Optional[List[Author]] = None,
        venue: Optional[str] = None,
        abstract: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        doi: Optional[str] = None,
        pdf_link: Optional[Union[List[str], str]] = None,
        year: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.title = title
        self.authors = authors
        self.venue = venue
        self.abstract = abstract
        self.keywords = keywords
        self.doi = doi
        self.pdf_link = pdf_link
        self.year = year

    def load_from_json(self, json_path: str) -> None:
        assert os.path.exists(json_path)
        assert json_path.endswith(".json")
        with open(json_path) as f:
            info = json.load(f)

        pass

    def dict(self) -> Dict[str, Any]:
        pub = dict()
        pub["title"] = self.title
        if self.authors is not None:
            pub["authors"] = [a.dict() for a in self.authors]
        if self.venue is not None:
            pub["venue"] = self.venue
        if self.abstract is not None:
            pub["abstract"] = self.abstract
        if self.keywords is not None:
            pub["keywords"] = self.keywords
        if self.doi is not None:
            pub["doi"] = self.doi
        if self.pdf_link is not None:
            pub["pdf_link"] = self.pdf_link
        if self.year is not None:
            pub["year"] = self.year
        return pub

    def to_json(self, json_path: str) -> None:

        pass


class BaseCrawler(object):
    def __init__(
        self, headless=True, binary_location="/usr/bin/chrome-linux/chrome"
    ) -> None:
        super().__init__()

        if headless:
            self.chrome_options = Options()
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--no-gpu")
            self.chrome_options.add_argument("--disable-setuid-sandbox")
            self.chrome_options.add_argument("--single-process")
            self.chrome_options.add_argument("--window-size=1920,1080")
            self.chrome_options.binary_location = binary_location
            self.driver = webdriver.Chrome(chromedriver, options=self.chrome_options)
        else:
            self.driver = webdriver.Chrome()

    @staticmethod
    def open_url_in_new_tab(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self: BaseCrawler = args[0]
            url: str = args[1]

            current_handle_index = self.driver.window_handles.index(
                self.driver.current_window_handle
            )
            self.driver.execute_script('window.open("{}","_blank"' % url)
            self.driver.switch_to.window(self.driver.window_handles[-1])

            result = func(*args, **kwargs)

            self.driver.close()
            self.driver.switch_to(self.driver.window_handles[current_handle_index])
            return result

        return wrapper

    @staticmethod
    def random_sleep(min=5, max=20):
        def decorate(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                time.sleep(random.uniform(min, max))
                return result

            return wrapper

        return decorate

    def search_publication(self, title: str):
        raise NotImplementedError

    def search_author(self, name: str):
        raise NotImplementedError


class AMinerCrawler(BaseCrawler):
    def __init__(self, headless=True) -> None:
        super().__init__(headless=headless)

    @BaseCrawler.random_sleep()
    def search_publication(self, title: str):
        self.driver.get("https://www.aminer.org/search/pub?q={}".format(title))

        try:
            element_present = EC.presence_of_element_located(
                (By.CLASS_NAME, "title-link")
            )
            WebDriverWait(self.driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        finally:
            print("Page loaded")

        first_match = self.driver.find_element_by_class_name("title-link")

        next_page = self.driver.find_element_by_xpath("//li[@title='Next Page']")
        prev_page = self.driver.find_element_by_xpath("//li[@title='Previous Page']")

        first_match.click()
        current_window = self.driver.current_window_handle
        self.driver.switch_to.window(self.driver.window_handles[-1])

        with open("before.html", "w") as f:
            f.write(self.driver.page_source)

        try:
            element_present = EC.presence_of_element_located(
                (By.CLASS_NAME, "titleline")
            )
            WebDriverWait(self.driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        finally:
            print("Page loaded")

        with open("after.html", "w") as f:
            f.write(self.driver.page_source)

        # find meta info in page source code
        pattern = re.compile(
            r"window\.g_initialProps = (.*?);$", re.MULTILINE | re.DOTALL
        )

        info = eval(
            re.findall(pattern, self.driver.page_source)[0]
            .replace("false", "False")
            .replace("true", "True")
            .replace("undefined", "None")
        )
        pprint(info)
        pub = self.build_pub_from_dict(info)
        pprint(pub.dict())

        self.driver.close()
        self.driver.switch_to.window(current_window)
        return info

    def build_pub_from_dict(self, info: Dict[str, Any]):
        assert "paper" in info.keys()
        paper: Dict[str, Any] = info["paper"]

        assert "title" in paper.keys()
        title = paper["title"]

        abstract = paper.get("abstract")
        doi = paper.get("doi")
        pdf_link = paper.get("pdf")
        authors = paper.get("authors")
        year = paper.get("year")
        venue = paper.get("venue")
        keywords = paper.get("keywords")

        if authors is not None:
            authors = [self.build_author_from_dict(a) for a in authors]

        return Publication(
            title,
            authors=authors,
            venue=venue,
            abstract=abstract,
            keywords=keywords,
            doi=doi,
            pdf_link=pdf_link,
            year=year,
        )

    def build_author_from_dict(self, info: Dict[str, Any]):
        assert "name" in info.keys()
        return Author(info["name"])

    def search_author(self, name: str):
        return super().search_author(name)


if __name__ == "__main__":
    aminer = AMinerCrawler()
    out = aminer.search_publication(
        "Imbalanced gradients: A new cause of overestimated adversarial robustness"
    )
    aminer.driver.quit()
