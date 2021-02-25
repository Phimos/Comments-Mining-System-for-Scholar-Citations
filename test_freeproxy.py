from crawlers.freeproxy import FreeProxyPool
from crawlers.freeproxy.proxynova import ProxyNova
from crawlers.freeproxy.sslproxies import SSLProxies


# proxynova = ProxyNova()
# out = proxynova.get_proxies()
# print(out)

sslproxies = SSLProxies()
sslproxies.get_proxies()
fp = FreeProxyPool()

