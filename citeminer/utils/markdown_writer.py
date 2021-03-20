from typing import List, Union, Optional
from citeminer.types import Publication, Author
import os


class Markdown(object):
    def __init__(self) -> None:
        super().__init__()

    @property
    def stream(self) -> str:
        return ""

    def __str__(self) -> str:
        return self.stream

    def __repr__(self) -> str:
        return self.stream

    def transform(self, text: str) -> str:
        text = text.replace("*", "\*")
        text = text.replace("`", "\`")
        text = text.replace("_", "\_")
        text = text.replace("{", "\{")
        text = text.replace("}", "\}")
        text = text.replace("[", "\[")
        text = text.replace("]", "\]")
        text = text.replace("(", "\(")
        text = text.replace(")", "\)")
        text = text.replace("#", "\#")
        text = text.replace("+", "\+")
        text = text.replace("-", "\-")
        text = text.replace("!", "\!")
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        return text


class SingleLineBreak(Markdown):
    def __init__(self) -> None:
        super().__init__()

    @property
    def stream(self) -> str:
        return " \n"


class DoubleLineBreak(Markdown):
    def __init__(self) -> None:
        super().__init__()

    @property
    def stream(self) -> str:
        return "\n \n"


class Space(Markdown):
    def __init__(self) -> None:
        super().__init__()

    @property
    def stream(self) -> str:
        return " "


class PlainText(Markdown):
    def __init__(self, text: str, endline: bool = True) -> None:
        super().__init__()
        self.text = text
        self.endline = endline

    @property
    def stream(self) -> str:
        if self.endline:
            return self.text + "\n"
        else:
            return self.text


class Header(Markdown):
    def __init__(self, text: Union[str, Markdown], level: int = 2) -> None:
        super().__init__()
        if isinstance(text, Markdown):
            self.text = text.stream
        else:
            self.text = text
        self.level = level

    @property
    def stream(self):
        return "#" * self.level + " " + self.text + "\n"


class Hyperlink(Markdown):
    def __init__(self, link_text: str, link_url: str) -> None:
        super().__init__()
        self.link_text = link_text
        self.link_url = link_url

    @property
    def stream(self):
        return "[" + self.link_text + "]" + "(" + self.link_url + ")"


class Emphasis(Markdown):
    def __init__(self, text: str, endline=True) -> None:
        super().__init__()
        self.text = text
        self.endline = endline

    @property
    def stream(self) -> str:
        if self.endline:
            return "*" + self.text + "*" + "\n"
        else:
            return "*" + self.text + "*"


class Strong(Markdown):
    def __init__(self, text: str, endline: bool = True) -> None:
        super().__init__()
        self.text = text
        self.endline = endline

    @property
    def stream(self) -> str:
        if self.endline:
            return "**" + self.text + "**" + "\n"
        else:
            return "**" + self.text + "**"


class Sequence(Markdown):
    def __init__(self, text_list: List[Markdown]) -> None:
        super().__init__()
        self.text_list = text_list

    @property
    def stream(self) -> str:
        return "".join([item.stream for item in self.text_list])


class CitingPublication(Markdown):
    def __init__(self, publication: Publication) -> None:
        super().__init__()
        self.title = publication["bib"]["title"]
        if publication["filled"]:
            self.author = publication["bib"]["author"]
        else:
            self.author = ", ".join(publication["bib"]["author"])

        if "journal" in publication["bib"].keys():
            self.journal_or_book = publication["bib"]["journal"]
            self.in_journal = True
        elif "booktitle" in publication["bib"].keys():
            self.journal_or_book = publication["bib"]["booktitle"]
            self.in_journal = False
        else:  # todo: fix it
            self.journal_or_book = "Unknown"
            self.in_journal = True

        self.abstract = publication["bib"]["abstract"]

        self.pdf_link = publication["pub_url"]

        if "http" not in self.pdf_link:
            self.pdf_link = os.path.abspath(self.pdf_link).replace(" ", "%20")

    @property
    def stream(self) -> str:
        return Sequence(
            [
                Header(
                    Hyperlink(self.title, self.pdf_link)
                    if self.pdf_link is not None
                    else PlainText(self.title)
                ),
                SingleLineBreak(),
                Emphasis("Author:", endline=False),
                Space(),
                PlainText(self.author),
                SingleLineBreak(),
                Emphasis(
                    "Journal:" if self.in_journal else "Booktitle:", endline=False
                ),
                Space(),
                PlainText(self.journal_or_book),
                SingleLineBreak(),
                Emphasis("Abstruct:"),
                Space(),
                SingleLineBreak(),
                PlainText(self.abstract),
                DoubleLineBreak(),
            ]
        ).stream


class CitingDocument(Markdown):
    def __init__(
        self,
        cited: Union[Publication, str] = "",
        publications: Optional[List[Publication]] = None,
        document_path: str = "summary.md",
    ) -> None:
        super().__init__()
        self.publications = publications if publications is not None else []
        if isinstance(cited, str):
            self.cited_publication = cited
        else:
            self.cited_publication = cited["bib"]["title"]
        self.path = document_path

    @property
    def stream(self):
        return Sequence(
            [
                Header(self.cited_publication, level=1),
                DoubleLineBreak(),
                *[CitingPublication(publication=pub) for pub in self.publications],
            ]
        ).stream

    def add_publication(self, pub: Publication) -> None:
        self.publications.append(pub)

    def save(self):
        with open(self.path, "w") as summary_file:
            summary_file.write(self.stream)


if __name__ == "__main__":
    pub = {
        "author_id": ["nRQi4O8AAAAJ", "bW6qGV0AAAAJ", "XqLiBQMAAAAJ", "nujTx04AAAAJ"],
        "bib": {
            "abstract": "This article is about a curious phenomenon. Suppose we "
            "have a data matrix, which is the superposition of a "
            "low-rank component and a sparse component. Can we "
            "recover each component individually? We prove that under "
            "some suitable assumptions, it is possible to",
            "author": "Cand{\\`e}s, Emmanuel J and Li, Xiaodong and Ma, Yi and "
            "Wright, John",
            "bib_id": "candes2011robust",
            "journal": "Journal of the ACM (JACM)",
            "number": "3",
            "pages": "1--37",
            "pub_type": "article",
            "pub_year": "2011",
            "publisher": "ACM New York, NY, USA",
            "title": "Robust principal component analysis?",
            "venue": "Journal of the ACM (JACM)",
            "volume": "58",
        },
        "citedby_url": "/scholar?cites=9000237782786002248&as_sdt=2005&sciodt=0,5&hl=en",
        "eprint_url": "https://arxiv.org/pdf/0912.3599",
        "filled": True,
        "gsrank": 1,
        "num_citations": 5637,
        "pub_url": "https://dl.acm.org/doi/abs/10.1145/1970392.1970395",
        "source": "PUBLICATION_SEARCH_SNIPPET",
        "url_add_sclib": "/citations?hl=en&xsrf=&continue=/scholar%3Fhl%3Den%26as_sdt%3D0,5%26sciodt%3D0,5%26cites%3D17633993505446855025%26scipsc%3D&citilm=1&json=&update_op=library_add&info=SE0CAZRE53wJ&ei=6tMUYNK0KI7MyAS7vZPQDA",
        "url_scholarbib": "/scholar?q=info:SE0CAZRE53wJ:scholar.google.com/&output=cite&scirp=0&hl=en",
    }
    with open("test.md", "w") as f:
        f.write(CitingPublication(pub).stream)

    print("hello")
