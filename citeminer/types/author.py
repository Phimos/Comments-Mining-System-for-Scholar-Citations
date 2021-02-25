from dataclasses import dataclass
from enum import Enum, unique


@unique
class AuthorSource(Enum):
    AUTHOR_PROFILE_PAGE = 1
    SEARCH_AUTHOR_SNIPPETS = 2
    CO_AUTHORS_LIST = 3


@dataclass
class Author(object):
    name: str
