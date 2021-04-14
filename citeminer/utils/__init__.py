import json
import os
from copy import deepcopy
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple

from citeminer.pdfparser.pdf2txt import extract_text
from fuzzywuzzy import fuzz, process


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


def convert2txt(task: Tuple, pdf_dir: str, txt_dir: str) -> None:
    author, pub, cpub = task

    pdf_path = os.path.join(
        pdf_dir, author, "publications", pub, "cited", cpub + ".pdf"
    )
    txt_path = os.path.join(
        txt_dir, author, "publications", pub, "cited", cpub + ".txt"
    )

    if not os.path.exists(pdf_path):
        return
    if os.path.exists(txt_path):
        return

    try:
        os.makedirs(os.path.dirname(txt_path), exist_ok=True)
        extract_text(files=[pdf_path], outfile=txt_path)
    except:
        pass


def generate_summary(task: Tuple) -> None:
    pass


def fill_pub_info(task: Tuple) -> None:
    pass


def download_pdf(task: Tuple) -> None:
    pass
