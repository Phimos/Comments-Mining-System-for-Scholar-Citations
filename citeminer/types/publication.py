from dataclasses import dataclass
from enum import Enum, unique


@dataclass
class Publication(object):
    name: str
