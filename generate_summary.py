import os
import json
from typing import Callable, Optional
from citeminer.pdfparser.pdf2txt import extract_text
from citeminer.utils.markdown_writer import CitingDocument

metadata_dir = "./result/metadata"
pdfs_dir = "./result/pdfs"
txts_dir = "./result/txts"


def go_allfiles(
    root: str,
    depth: int = -1,
    postfix: Optional[str] = None,
    func: Callable = lambda x: print(x),
) -> None:
    for subdir in os.listdir(root):
        if os.path.isdir(os.path.join(root, subdir)):
            if depth == 0:
                return
            else:
                go_allfiles(os.path.join(root, subdir), depth - 1, postfix, func)
        else:
            if (postfix is None or subdir.endswith(postfix)) and (depth <= 0):
                func(os.path.join(root, subdir))


def convert2txt(pdf_path: str) -> None:
    try:
        txt_path = pdf_path.replace(pdfs_dir, txts_dir).replace(".pdf", ".txt")
        if os.path.exists(txt_path):
            return
        os.makedirs(os.path.dirname(txt_path), exist_ok=True)
        extract_text(files=[pdf_path], outfile=txt_path)
    except:
        print("error!")


from citeminer.pdfparser.parser import PDFParser

parser = PDFParser()


def generate_summary(metadata_path: str) -> None:
    markdown_path = os.path.join(
        os.path.dirname(metadata_path).replace(metadata_dir, pdfs_dir), "summary.md"
    )
    with open(metadata_path) as f:
        cited_pub = json.load(f)
    cited_dir = os.path.join(os.path.dirname(metadata_path), "cited")
    pubs = []
    for metadata in os.listdir(cited_dir):
        with open(os.path.join(cited_dir, metadata)) as f:
            pub = json.load(f)

        pdf_path = metadata_path.replace(metadata_dir, pdfs_dir).replace(
            ".json", ".pdf"
        )

        if os.path.exists(pdf_path):
            pub["pub_url"] = os.path.abspath(pdf_path)

        pubs.append(pub)
        print(os.path.join(cited_dir, metadata))
        txt_path = (
            os.path.join(cited_dir, metadata)
            .replace(metadata_dir, txts_dir)
            .replace(".json", ".txt")
        )
        if os.path.exists(txt_path):
            print(parser.parse(txt_path, cited_pub))
            pass
        else:
            print("txt not exists")
    # todo: need to be fixed
    try:
        CitingDocument(cited_pub["bib"]["title"], pubs, markdown_path).save()
    except:
        pass


# go_allfiles(metadata_dir, depth=3, postfix=".json", func=generate_summary)

generate_summary(
    "./result/metadata/Yisen Wang/publications/A novel consistent random forest framework- Bernoulli random forests/A novel consistent random forest framework- Bernoulli random forests.json"
)

generate_summary(
    "./result/metadata/Zhouchen Lin/publications/Towards understanding adversarial examples systematically- Exploring data size, task and model factors/Towards understanding adversarial examples systematically- Exploring data size, task and model factors.json"
)
# go_allfiles(pdfs_dir, depth=4, postfix=".pdf", func=convert2txt)
