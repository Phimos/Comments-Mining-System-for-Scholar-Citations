import json
import os
from functools import partial
from typing import Any, Callable, List, Optional, Tuple

from citeminer.pdfparser.pdf2txt import extract_text


def dump_json(obj: Any, file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    fp = open(file_path, "w")
    json.dump(obj, fp, sort_keys=True, indent=4, separators=(",", ":"))


def generate_tasks(root_dir: str, task_type: str = "cpub") -> List[Any]:
    tasks: List[Any] = []
    assert task_type in ["author", "pub", "cpub"]

    if task_type == "author":
        for author in os.listdir(root_dir):
            tasks.append((author))

    elif task_type == "pub":
        for author in os.listdir(root_dir):
            pub_dir = os.path.join(root_dir, author, "publications")
            for pub in os.listdir(pub_dir):
                tasks.append((author, pub))

    elif task_type == "cpub":
        for author in os.listdir(root_dir):
            pub_dir = os.path.join(root_dir, author, "publications")
            for pub in os.listdir(pub_dir):
                cpub_dir = os.path.join(pub_dir, pub, "cited")
                for cpub in os.listdir(cpub_dir):
                    if cpub.endswith(".json"):
                        cpub = cpub[:-5]
                        tasks.append((author, pub, cpub))

    else:
        raise ValueError

    return tasks


def convert2txt(task: Tuple) -> None:
    author, pub, cpub = task
    pdf_dir = ""
    txt_dir = ""

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
