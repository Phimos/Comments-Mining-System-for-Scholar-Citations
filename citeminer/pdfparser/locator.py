import re
from os import replace
from typing import List, Optional

sentence_pattern = (
    "((\\([^\\(\\)]*\\))|(\\[[^\\[\\]]*\\])|(\\d+\\.\\d+)|[^\\(\\)\\[\\]])*\\."
)
single_index_pattern = "\\[(\\d+)\\]"
multi_index_pattern = "\\[[^\\[\\]]*[^\\d](\\d+)[^\\d]+[^\\[\\]]*\\]"

index_pattern = "\\[[^\\[\\]a-zA-Z\\.]+\\]"


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
        elif "–" in text:
            for left, right in re.findall("(\\d+)–(\\d+)", text):
                if int(left) <= int(index) <= int(right):
                    return True
            return False
        else:
            return False

    def split_sentences(self, block):
        # TODO: don't drop when the first block is needed
        # eg. A Topological Filter for Learning with Label Noise <- Dimensionality-Driven Learning with Noisy Labels
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
        for item in re.finditer(index_pattern, text, re.I):
            if self._check_index(item.group(), index):
                # Todo: replace it with better match algo
                comment_block = text[item.start() - 500 : item.end() + 500]
                comment_block = comment_block.replace(
                    item.group(), "**" + item.group() + "**"
                )
                clean_block = self.clean_comment_block(comment_block)
                comments.append(clean_block)
        return comments

    def _check_author(self, text: str, author: str, year: str) -> bool:
        # TODO: finish it
        return True

    def locate_by_author(
        self, text: str, author_last_name: str, year: str
    ) -> List[str]:
        comments = []
        author_pattern = (
            "[^a-zA-Z]" + author_last_name + "[^a-zA-Z]" + "[^\\d]{0,20}" + year
        )
        for item in re.finditer(author_pattern, text):
            if self._check_author(item.group(), author_last_name, year):
                comment_block = text[item.start() - 500 : item.end() + 500]
                comment_block = (
                    comment_block.replace(
                        item.group().strip(), "**" + item.group().strip() + "**"
                    )
                    .replace("(**", "**(")
                    .replace("[**", "**[")
                    .replace("**)", ")**")
                    .replace("**]", "]**")
                )
                clean_block = self.clean_comment_block(comment_block)
                comments.append(clean_block)
        return comments


if __name__ == "__main__":
    locator = CitationLocator()
    with open("aaa.txt") as f:
        text = f.read()
    text = text.replace("\n", " ")
    text = text.replace("- ", "")
    text = text.replace("ﬁ", "fi")

    for o in locator.locate_by_index(text, "44"):
        print(o)
        print()

    for o in locator.locate_by_author(text, "Ma", "2018"):
        print(o)
        print()

    for i in re.finditer(
        "Ma[^\\d]{0,20}2018",
        "dp, or storage limits, data turns are available for the limited duration. Moreover, in such scenarios, combating label noise adds to the challenge.  The prior art tries to enhance the robustness of the deep model training against noisy labels in the off-line scenario by (i) filtering out noisy data through model disagreement Han et al. [2018], Yu et al. [2019], (ii) correcting noisy labels through the estimated noisy corruption matrix Patrini et al. [2017], or (iii) modifying the loss functions Ma et al. [2018], Wang et al. [2019]. Among the related studies, high quality labels from human expert",
    ):
        print(i.group())
    # with open("e.txt") as f:
    #    text = f.read()
    # text = text.replace("\n", "")
    # locator.locate_by_author(text, "Wang", "2019")
    # pass
