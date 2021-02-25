#!/usr/bin/env python
print(
    "If you get error \"ImportError: No module named 'six'\" install six:\n"
    + "$ sudo pip install six"
)
print(
    "To enable your free eval account and get CUSTOMER, YOURZONE and "
    + "YOURPASS, please contact sales@luminati.io"
)
import sys
import urllib.request
import random
import requests

username = "lum-customer-hl_6a67d4c9-zone-static"
password = "n4etpkcfi5ee"
port = 22225
session_id = random.random()
super_proxy_url = "http://%s-session-%s:%s@zproxy.lum-superproxy.io:%d" % (
    username,
    session_id,
    password,
    port,
)

proxy = {"http": super_proxy_url, "https": super_proxy_url,}
print(
    {"http": super_proxy_url, "https": super_proxy_url,}
)
print("Performing request")
print(requests.get("https://scholar.google.com", proxies=proxy))

