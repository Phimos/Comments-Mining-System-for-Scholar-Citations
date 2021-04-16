from typing import Dict, List, Optional

from .extractor import IndexExtractor
from .locator import CitationLocator
from .pdf2txt import extract_text


class PDFParser(object):
    def __init__(self) -> None:
        super().__init__()
        self.extractor = IndexExtractor()
        self.locator = CitationLocator()

    def parse(self, file_path: str, info: Dict) -> List[str]:
        with open(file_path) as f:
            text = f.read()
        text = text.replace("\n", " ")
        text = text.replace("- ", "")
        text = text.replace("ﬁ", "fi")

        index_type, index = self.extractor.extract(text, info["bib"]["title"])

        if index_type != "none":
            comments = self.locator.locate_by_index(text, index)
            if index_type == "bracket":
                return comments[:-1]
            else:
                return comments

        else:
            return []
            return self.locator.locate_by_author(
                text, info["bib"]["author"][0], info["bib"]["pub_year"]
            )
