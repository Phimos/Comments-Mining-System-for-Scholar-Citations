import re


class IndexExtractor(object):
    def __init__(self) -> None:
        super().__init__()

    def extract(self, text: str, title: str) -> str:
        words = "".join(re.findall("\\w+", title))
        pattern = "(\\d+\\.[^\\d]*"
        pass
