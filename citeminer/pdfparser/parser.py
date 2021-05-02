import re
from typing import Dict, List, Optional

from .extractor import IndexExtractor
from .locator import CitationLocator
from .pdf2txt import extract_text


class PDFParser(object):
    def __init__(self) -> None:
        super().__init__()
        self.extractor = IndexExtractor()
        self.locator = CitationLocator()

    def delete_reference_line(self, comments: List[str], title: str) -> List[str]:
        result = []
        pattern = IndexExtractor.title_pattern(title)
        for comment in comments:
            if re.search(pattern, comment, re.I | re.U):
                pass
            else:
                result.append(comment)
        return result

    def parse(self, file_path: str, info: Dict) -> List[str]:
        with open(file_path) as f:
            text = f.read()
        text = text.replace("\n", " ")
        text = text.replace("- ", "")
        text = text.replace("ﬁ", "fi")

        index_type, index = self.extractor.extract(text, info["bib"]["title"])
        # TODO: filter the index one with bib title
        if index_type != "none":
            comments = self.locator.locate_by_index(text, index)
            return self.delete_reference_line(comments, info["bib"]["title"])

        elif "author" in info["bib"].keys() and "pub_year" in info["bib"].keys():
            authors: str = info["bib"]["author"]
            first_author = authors.split("and")[0].strip()
            last_name = first_author.split(" ")[-1].strip()
            pub_year = info["bib"]["pub_year"]
            return self.locator.locate_by_author(text, last_name, pub_year)

        else:
            return []
