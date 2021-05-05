from .allinone import AllInOneDownloader
from .base import BaseDownlaoder
from .dummy import DummyDownloader
from .ieee_downloader import HindawiDownloader, IEEEDownloader
from .scihub import SciHub, SciHubDownloader
from .simple import SimpleDownloader

__all__ = [
    "SciHub",
    "SimpleDownloader",
    "AllInOneDownloader",
    "HindawiDownloader",
    "DummyDownloader",
    "IEEEDownloader",
    "SciHubDownloader",
]
