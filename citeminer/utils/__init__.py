import json
import os
from typing import Any, Callable, List, Optional


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
                    assert cpub.endswith(".json")
                    cpub = cpub[:-5]
                    tasks.append((author, pub, cpub))

    else:
        raise ValueError

    return tasks
