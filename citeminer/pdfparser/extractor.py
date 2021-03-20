import re
from typing import Optional

from citeminer import debug


class IndexExtractor(object):
    def __init__(self) -> None:
        super().__init__()

    def extract_bracket(self, text: str, title: str) -> Optional[str]:
        words = re.findall(r"\w+", title)
        words = list("".join(words))
        pattern = "\\[\\s*\\d+\\s*\\][^\\[\\]]{0,200}" + "\\W*".join(words)
        result = re.search(pattern, text, re.I | re.U)
        if result:
            citation = result.group()
            citation_idx = re.findall("\\[[^\\d]*(\\d*)[^\\d]*\\]", citation)[0]
            return citation_idx
        else:
            return None

    def extract_dot(self, text: str, title: str) -> Optional[str]:
        words = re.findall(r"\w+", title)
        words = list("".join(words))
        pattern = "\\d+\\.(([^\\d]\\.)|([^\\.]))*" + "\\W*".join(words)
        result = re.search(pattern, text, re.I | re.U)
        if result:
            citation = result.group()
            citation_idx = re.findall("(\\d+)\\.", citation)[0]
            return citation_idx
        else:
            return None

    def extract(self, text: str, title: str) -> Optional[str]:
        citation_idx = self.extract_bracket(text, title)
        if citation_idx is not None:
            return citation_idx
        citation_idx = self.extract_dot(text, title)
        if citation_idx is not None:
            return citation_idx
        return None


if __name__ == "__main__":
    extractor = IndexExtractor()
    with open("h.txt") as f:
        text = f.read()
    text.replace("\n", "")
    print(
        extractor.extract(
            text, "A novel consistent random forest framework: Bernoulli random forests"
        )
    )
