import requests
import pandas as pd
import sys
import logging


def init_logger() -> logging.Logger:
    logger = logging.getLogger("free-proxy")
    logger.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S",
    )
    stdout_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)
    return logger


class BaseProxiesCrawler(object):
    logger = init_logger()

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def empty_proxies(self) -> pd.DataFrame:
        return pd.DataFrame(columns=["ip address", "port"])
