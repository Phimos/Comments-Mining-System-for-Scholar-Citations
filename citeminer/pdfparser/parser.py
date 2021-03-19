from typing import List
from .locator import CitationLocator
from .extractor import IndexExtractor
from .pdf2txt import extract_text
from typing import Optional, List


class PDFParser(object):
    def __init__(self) -> None:
        super().__init__()
        self.extractor = IndexExtractor()
        self.locator = CitationLocator()


    def parser(self, file_path: str) -> Optional[List[str]]:
        title = ''
        text = ''
        
        index = self.extractor.extract(text, title)
        if self.index_citation():


        return None
