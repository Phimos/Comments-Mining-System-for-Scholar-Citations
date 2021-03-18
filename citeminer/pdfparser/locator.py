import re
from typing import Optional, List


sentece_pattern = "[^\\.]*\\."
single_index_pattern = "\\[(\\d+)\\]"
multi_index_pattern = "\\[[^\\[\\]]*[^\\d](\\d+)[^\\d]+[^\\[\\]]*\\]"


class CitationLocator(object):
    def __init__(self) -> None:
        super().__init__()

    def locate(
        self,
        doc: str,
        index: Optional[str] = None,
        first_author: Optional[str] = None,
        pub_year: Optional[int] = None,
        index_type: str = "bracket",
    ) -> List[str]:
        if index_type == "bracket":
            pass
        elif index_type == "author":
            pass
        else:
            raise ValueError

    def locate_by_index(self, doc: str, index: str):
        pass

    def locate_by_author(self, doc: str, author: str, year: int):
        pass


if __name__ == "__main__":
    pass