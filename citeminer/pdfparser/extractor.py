import re
from typing import Optional, Tuple

from citeminer import debug


class IndexExtractor(object):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def title_pattern(title: str) -> str:
        words = re.findall(r"\w+", title)
        words = list("".join(words))
        return "\\W*".join(words)

    def extract_bracket(self, text: str, title: str) -> Optional[str]:
        pattern = "\\[\\s*\\d+\\s*\\][^\\[\\]]{0,200}" + self.title_pattern(title)
        result = re.search(pattern, text, re.I | re.U)
        if result:
            citation = result.group()
            citation_idx = re.findall("\\[[^\\d]*(\\d*)[^\\d]*\\]", citation)[0]
            return citation_idx
        else:
            return None

    def extract_dot(self, text: str, title: str) -> Optional[str]:
        pattern = "\\d+\\.(([^\\d]\\.)|([^\\.]))*" + self.title_pattern(title)
        result = re.search(pattern, text, re.I | re.U)
        if result:
            citation = result.group()
            citation_idx = re.findall("(\\d+)\\.", citation)[0]
            return citation_idx
        else:
            return None

    def extract(self, text: str, title: str) -> Tuple[str, str]:
        citation_idx = self.extract_bracket(text, title)
        if citation_idx is not None and len(citation_idx) < 4:
            return "bracket", citation_idx
        citation_idx = self.extract_dot(text, title)
        if citation_idx is not None and len(citation_idx) < 4:
            return "dot", citation_idx
        return "none", ""


if __name__ == "__main__":
    extractor = IndexExtractor()
    with open("a.txt") as f:
        text = f.read()
    text = text.replace("\n", " ")
    text = text.replace("- ", "")
    text = text.replace("ﬁ", "fi")
    print(
        extractor.extract(
            text,
            "Improving Adversarial Robustness Requires Revisiting Misclassified Examples",
        )
    )
