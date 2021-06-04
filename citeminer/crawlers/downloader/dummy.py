import os
from typing import Any

import filetype

from .base import BaseDownlaoder


class DummyDownloader(BaseDownlaoder):
    priority = 0

    def __init__(self) -> None:
        super().__init__()

    def _valid_pdf_file(self, path: str) -> bool:
        result = filetype.guess(path)
        return result is not None and result.mime == "application/pdf"

    def download(self, url: str, path: str, **kwargs: Any) -> bool:
        if os.path.exists(path) and self._valid_pdf_file(path):
            return True
        else:
            return False
