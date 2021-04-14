import re
from os import replace
from typing import List, Optional

sentence_pattern = (
    "((\\([^\\(\\)]*\\))|(\\[[^\\[\\]]*\\])|(\\d+\\.\\d+)|[^\\(\\)\\[\\]])*\\."
)
single_index_pattern = "\\[(\\d+)\\]"
multi_index_pattern = "\\[[^\\[\\]]*[^\\d](\\d+)[^\\d]+[^\\[\\]]*\\]"

index_pattern = "\\[[^\\[\\]a-zA-Z]+\\]"
single_author_pattern = "[a-zA-Z\\s\\.\\&]+,\\s\\d{4}"
author_pattern = (
    "\\(" + single_author_pattern + "(" + ";" + single_author_pattern + ")*" + "\\)"
)


class CitationLocator(object):
    def __init__(self) -> None:
        super().__init__()

    def _check_index(self, text: str, index: str) -> bool:
        indices = re.findall("\\d+", text)
        if index in indices:
            return True
        elif "-" in text:
            for left, right in re.findall("(\\d+)-(\\d+)", text):
                if int(left) <= int(index) <= int(right):
                    return True
            return False
        else:
            return False

    def split_sentences(self, block):
        sentence_pattern = "[^\.]*\."
        result = []
        for i, s in enumerate(re.findall(sentence_pattern, block)):
            if i == 0:
                result.append(s)
                continue

            if s[0] == "," or not " " in s.strip():
                result[-1] = result[-1] + s
            else:
                result.append(s)

        result = result[1:]
        result = [s.strip() for s in result]
        return result

    def clean_comment_block(self, comment_block):
        return " ".join(self.split_sentences(comment_block))

    def locate_by_index(self, text: str, index: str) -> List[str]:
        comments = []
        for item in re.finditer(index_pattern, text):
            if self._check_index(item.group(), index):
                # Todo: replace it with better match algo
                comment_block = text[item.start() - 500 : item.end() + 500]
                comment_block = comment_block.replace(
                    item.group(), "**" + item.group() + "**"
                )
                # comment_block = re.search(
                #    sentence_pattern
                #    + "((\\([^\\(\\)]*\\))|(\\[[^\\[\\]]*\\])|(\\d+\\.\\d+)|[^\\(\\)\\[\\]])*"
                #    + item.group().replace("[", "\\[").replace("]", "\\]")
                #    + sentence_pattern
                #    + sentence_pattern,
                #    comment_block,
                # ).group()
                clean_block = self.clean_comment_block(comment_block)
                comments.append(clean_block)
        return comments

    def _check_author(self, text: str, author: str, year: str) -> bool:
        for single_author in re.findall(single_author_pattern, text):
            if author in single_author and year in single_author:
                return True
        return False

    def locate_by_author(self, text: str, author: str, year: str) -> List[str]:
        comments = []
        for item in re.finditer(author_pattern, text):
            if self._check_author(item.group(), author, year):
                comments.append(text[item.start() - 500 : item.end() + 100])
        return comments


if __name__ == "__main__":
    locator = CitationLocator()
    with open("c.txt") as f:
        text = f.read()
    text = text.replace("\n", "")

    print(locator.locate_by_index(text, "19"))

    with open("e.txt") as f:
        text = f.read()
    text = text.replace("\n", "")
    locator.locate_by_author(text, "Wang", "2019")
    pass
