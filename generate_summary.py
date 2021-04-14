#%%
import json
import os
from typing import Callable, Optional

from eventlet import Timeout

from citeminer.crawlers import scholar
from citeminer.crawlers.scholar import ProxyGenerator, scholarly
from citeminer.pdfparser.pdf2txt import extract_text
from citeminer.utils.markdown_writer import CitingDocument

metadata_dir = "./result/metadata"
aminer_info_dir = "./result/aminer"
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

        if not pub["filled"] and os.path.exists(
            os.path.join(cited_dir, metadata).replace(metadata_dir, aminer_info_dir)
        ):
            with open(
                os.path.join(cited_dir, metadata).replace(metadata_dir, aminer_info_dir)
            ) as f:
                aminer_info = json.load(f)
            if (
                fuzz.token_set_ratio(
                    pub["bib"]["title"].lower(), aminer_info["paper"]["title"].lower()
                )
                >= 85
            ) and "authors" in aminer_info["paper"].keys():
                pub["bib"]["author"] = [
                    a["name"] for a in aminer_info["paper"]["authors"]
                ]
                if (
                    "venue" in aminer_info["paper"].keys()
                    and "info" in aminer_info["paper"]["venue"].keys()
                    and "name" in aminer_info["paper"]["venue"]["info"].keys()
                ):
                    pub["bib"]["journal"] = aminer_info["paper"]["venue"]["info"][
                        "name"
                    ]
                    print(pub["bib"]["journal"])
                if "abstract" in aminer_info["paper"].keys():
                    pub["bib"]["abstract"] = aminer_info["paper"]["abstract"]

        pdf_path = (
            os.path.join(cited_dir, metadata)
            .replace(metadata_dir, pdfs_dir)
            .replace(".json", ".pdf")
        )

        if os.path.exists(pdf_path):
            pub["pub_url"] = os.path.abspath(pdf_path)

        # print(os.path.join(cited_dir, metadata))
        txt_path = (
            os.path.join(cited_dir, metadata)
            .replace(metadata_dir, txts_dir)
            .replace(".json", ".txt")
        )

        comments = []
        if os.path.exists(txt_path):
            comments = parser.parse(txt_path, cited_pub)
        else:
            # print("txt not exists")
            pass

        pubs.append({"publication": pub, "comments": comments})
        # pubs.append({"publication": pub})
    # todo: need to be fixed
    try:
        CitingDocument(cited_pub["bib"]["title"], pubs, markdown_path).save()
    except:
        pass


scholar_crawler = scholarly
pg = ProxyGenerator()
pg.SingleProxy(http="http://127.0.0.1:24000", https="http://127.0.0.1:24000")
scholar_crawler.use_proxy(pg)


def fill_info(metadata_path):
    with open(metadata_path) as f:
        info = json.load(f)
    if not info["filled"] and "title" in info["bib"].keys():
        print(info["bib"]["title"])
        try:
            with Timeout(60, False):
                search_query = scholar_crawler.search_pubs(info["bib"]["title"])
                fullinfo = scholar_crawler.fill(next(search_query))
                dict_info = scholar_crawler.get_pprint(fullinfo)
                with open(metadata_path, "w") as outfile:
                    json.dump(
                        dict_info,
                        outfile,
                        sort_keys=True,
                        indent=4,
                        separators=(",", ":"),
                    )
                print(metadata_path, "saved.")
        except:
            print("[failed]", metadata_path)


from citeminer.crawlers.aminer import AMinerCrawler


def aminer_info(metadata_path):
    with open(metadata_path) as f:
        info = json.load(f)
    title = info["bib"]["title"]
    try:
        aminer_path = metadata_path.replace(metadata_dir, aminer_info_dir)
        if os.path.exists(aminer_path):
            return
        aminer = AMinerCrawler()
        out = aminer.search_publication(title)
        aminer.driver.quit()
        pardir, _ = os.path.split(aminer_path)
        os.makedirs(pardir, exist_ok=True)
        with open(metadata_path.replace(metadata_dir, aminer_info_dir), "w") as outfile:
            json.dump(out, outfile, indent=2)
    except:
        pass


# cnt = 0
# ncnt = 0
#
#
# def count_aminer(metadata_path):
#    global cnt
#    global ncnt
#    aminer_path = metadata_path.replace(metadata_dir, aminer_info_dir)
#    if os.path.exists(aminer_path):
#        cnt += 1
#    else:
#        ncnt += 1
#
#
# go_allfiles(metadata_dir, depth=4, postfix=".json", func=count_aminer)
# print(cnt, ncnt)


import matplotlib.pyplot as plt
from fuzzywuzzy import fuzz

rs = []


def find_unmatched_pair(metadata_path):
    global rs
    with open(metadata_path) as f:
        ori_info = json.load(f)
    ori_title = ori_info["bib"]["title"]
    aminer_path = metadata_path.replace(metadata_dir, aminer_info_dir)
    if not os.path.exists(aminer_path):
        return
    with open(aminer_path) as f:
        aminer_info = json.load(f)
    aminer_title = aminer_info["paper"]["title"]
    r = fuzz.token_set_ratio(ori_title.lower(), aminer_title.lower())
    rs.append((r, metadata_path))


go_allfiles(pdfs_dir, depth=4, postfix=".pdf", func=convert2txt)

go_allfiles(metadata_dir, depth=4, postfix=".json", func=aminer_info)

go_allfiles(metadata_dir, depth=3, postfix=".json", func=generate_summary)
