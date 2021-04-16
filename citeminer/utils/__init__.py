import json
import os
from copy import deepcopy
from functools import partial
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

import requests
from citeminer.crawlers.aminer import AMinerCrawler
from citeminer.pdfparser.pdf2txt import extract_text
from citeminer.utils.markdown_writer import CitingDocument
from fuzzywuzzy import fuzz, process
from tqdm import tqdm


def apply_func(func: Callable, iterator: Iterable) -> None:
    for item in tqdm(iterator):
        func(item)


# Json Load & Dump


def dump_json(obj: Any, file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    fp = open(file_path, "w")
    json.dump(obj, fp, sort_keys=True, indent=4, separators=(",", ":"))
    fp.close()


def load_json(file_path: str) -> Dict[str, Any]:
    assert file_path.endswith(".json")
    fp = open(file_path)
    result = json.load(fp)
    fp.close()
    return result


# Fuzzy Match


def fuzzy_match(str1: str, str2: str, threshold: int = 85) -> bool:
    str1 = str1.lower()
    str2 = str2.lower()
    return fuzz.ratio(str1, str2) >= threshold


def fuzzy_extract_one(
    query: str,
    choices: List[str],
    scorer: Callable = fuzz.token_set_ratio,
    threshold: int = 85,
) -> Tuple[bool, str]:
    ret = process.extractOne(query, choices, scorer=scorer, score_cutoff=threshold)
    if ret is not None:
        return True, ret[0]
    else:
        return False, ""


# Config Control


def search_metadata_dir(root_dir: str) -> Dict[str, Dict[str, List]]:
    result: Dict = {}
    for author in os.listdir(root_dir):
        result[author] = {}
        pub_dir = os.path.join(root_dir, author, "publications")
        for pub in os.listdir(pub_dir):
            result[author][pub] = []
            cpub_dir = os.path.join(pub_dir, pub, "cited")
            for cpub in os.listdir(cpub_dir):
                cpub, *_ = os.path.splitext(cpub)
                result[author][pub].append(cpub)
    return result


def merge_local_user_data(
    local_data: Dict[str, Dict[str, List]], user_guide: List[Dict[str, Any]]
) -> Dict[str, Dict[str, List]]:
    result: Dict = {}
    for author_info in user_guide:
        ok, author = fuzzy_extract_one(author_info["name"], list(local_data.keys()))
        if not ok:
            continue

        if "publications" not in author_info.keys():
            result[author] = deepcopy(local_data[author])
        else:
            result[author] = {}
            for pub_name in author_info["publications"]:
                ok, pub = fuzzy_extract_one(pub_name, list(local_data[author].keys()))
                if ok:
                    result[author][pub] = deepcopy(local_data[author][pub])
    return result


def generate_tasks(
    root_dir: str,
    task_type: str = "cpub",
    user_guide_info: Optional[List] = None,
) -> List[Any]:
    tasks: List[Any] = []
    data = search_metadata_dir(root_dir)
    if user_guide_info is not None:
        data = merge_local_user_data(data, user_guide_info)

    assert task_type in ["author", "pub", "cpub"]

    if task_type == "author":
        for author in data.keys():
            tasks.append((author))

    elif task_type == "pub":
        for author in data.keys():
            for pub in data[author].keys():
                tasks.append((author, pub))

    elif task_type == "cpub":
        for author in data.keys():
            for pub in data[author].keys():
                for cpub in data[author][pub]:
                    tasks.append((author, pub, cpub))

    else:
        raise ValueError

    return tasks


def get_cpub_path(root_dir: str, author: str, pub: str, cpub: str, postfix: str) -> str:
    return os.path.join(root_dir, author, "publications", pub, "cited", cpub + postfix)


def makepardirs(file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)


def convert2txt(task: Tuple, pdf_dir: str, txt_dir: str) -> None:
    """
    cpub level task
    """
    author, pub, cpub = task

    pdf_path = get_cpub_path(pdf_dir, author, pub, cpub, ".pdf")
    txt_path = get_cpub_path(txt_dir, author, pub, cpub, ".txt")

    if not os.path.exists(pdf_path) or os.path.exists(txt_path):
        return

    try:
        os.makedirs(os.path.dirname(txt_path), exist_ok=True)
        extract_text(files=[pdf_path], outfile=txt_path)
    except:
        pass


def generate_summary(
    task: Tuple, metadata_dir: str, pdf_dir: str, aminer_dir: str, txt_dir: str, parser
) -> None:
    """
    pub level task
    """
    author, pub = task

    markdown_path = os.path.join(pdf_dir, author, "publications", pub, "summary.md")
    json_path = os.path.join(metadata_dir, author, "publications", pub, pub + ".json")

    makepardirs(markdown_path)
    makepardirs(json_path)

    cited_dir = os.path.join(metadata_dir, author, "publications", pub, "cited")

    pub_info = load_json(json_path)

    cpubs = []
    for cpub in os.listdir(cited_dir):

        cpub_info = load_json(os.path.join(cited_dir, cpub))

        cpub, *_ = os.path.splitext(cpub)

        aminer_path = get_cpub_path(aminer_dir, author, pub, cpub, ".json")
        pdf_path = get_cpub_path(pdf_dir, author, pub, cpub, ".pdf")
        txt_path = get_cpub_path(txt_dir, author, pub, cpub, ".txt")

        if not cpub_info["filled"] and os.path.exists(aminer_path):
            aminer_info = load_json(aminer_path)
            if (
                fuzzy_match(cpub_info["bib"]["title"], aminer_info["paper"]["title"])
                and "authors" in aminer_info["paper"].keys()
            ):
                cpub_info["bib"]["author"] = [
                    a["name"] for a in aminer_info["paper"]["authors"]
                ]
                if (
                    "venue" in aminer_info["paper"].keys()
                    and "info" in aminer_info["paper"]["venue"].keys()
                    and "name" in aminer_info["paper"]["venue"]["info"].keys()
                ):

                    cpub_info["bib"]["journal"] = aminer_info["paper"]["venue"]["info"][
                        "name"
                    ]
                    # print(cpub_info["bib"]["journal"])
                if "abstract" in aminer_info["paper"].keys():
                    cpub_info["bib"]["abstract"] = aminer_info["paper"]["abstract"]

        if os.path.exists(pdf_path):
            cpub_info["pub_url"] = os.path.abspath(pdf_path)

        comments = []
        if os.path.exists(txt_path):
            comments = parser.parse(txt_path, pub_info)

        cpubs.append({"publication": cpub_info, "comments": comments})

    try:
        CitingDocument(pub_info["bib"]["title"], cpubs, markdown_path).save()
    except:
        pass


def fill_aminer_info(task: Tuple, metadata_dir: str, aminer_dir: str) -> None:
    """
    cpub level task
    """
    author, pub, cpub = task

    metadata_path = get_cpub_path(metadata_dir, author, pub, cpub, ".json")
    aminer_path = get_cpub_path(aminer_dir, author, pub, cpub, ".json")

    if not os.path.exists(metadata_path) or os.path.exists(aminer_path):
        return

    makepardirs(aminer_path)

    info = load_json(metadata_path)
    try:
        aminer = AMinerCrawler(proxy="http://127.0.0.1:24000")
        out = aminer.search_publication(info["bib"]["title"])
        aminer.driver.quit()
        dump_json(out, aminer_path)
    except:
        pass


def simple_download(url: str, path: str) -> bool:
    try:
        res = requests.get(url)
        if (
            "application/pdf" in res.headers["Content-Type"]
            or "application/octet-stream" in res.headers["Content-Type"]
            or "application/x-download" in res.headers["Content-Type"]
        ):
            with open(path, "wb") as f:
                f.write(res.content)
            return True
        else:
            return False
    except:
        return False


def scihub_download(scihub_crawler, url, path):
    return scihub_crawler.download(url, path=path)


def download_pdf(task: Tuple, metadata_dir: str, pdf_dir: str, scihub_crawler) -> None:
    """
    cpub level task
    """
    author, pub, cpub = task

    json_path = get_cpub_path(metadata_dir, author, pub, cpub, ".json")
    pdf_path = get_cpub_path(pdf_dir, author, pub, cpub, ".pdf")

    if not os.path.exists(json_path) or os.path.exists(pdf_path):
        return

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    info = load_json(json_path)
    if "pub_url" in info.keys():
        if "saved" in info.keys():
            if info["saved"] == "success":
                print("[&success]:", info["bib"]["title"])
                return
            else:
                print("[&failed]:", info["bib"]["title"])

        ok = False
        if "eprint_url" in info.keys():
            ok = simple_download(info["eprint_url"], path=pdf_path)
        if not ok:
            ok = scihub_download(scihub_crawler, info["pub_url"], path=pdf_path)

        status = "success" if ok else "failed"
        info["saved"] = status
        print("[%s]: %s" % (status, info["bib"]["title"]))

        dump_json(info, json_path)
