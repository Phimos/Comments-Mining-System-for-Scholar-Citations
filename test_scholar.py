from crawlers import scholarly, ProxyGenerator
import logging
from crawlers.freeproxy.freeproxy import FreeProxyPool


fp = FreeProxyPool(refresh=True, download=True)
print(fp.next_proxy())
