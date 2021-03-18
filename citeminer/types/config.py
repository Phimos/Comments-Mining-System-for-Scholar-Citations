from typing import List, Optional


class PublicationConfig(object):
    title: str
    year_start: Optional[int] = 2020
    year_end: Optional[int] = 2020


class AuthorConfig(object):
    name: str
    publications: Optional[List[PublicationConfig]] = None


class Config(object):
    timeout: int
    metadata_save_dir: str
    pdf_save_dir: str
    authors: Optional[List[AuthorConfig]]
