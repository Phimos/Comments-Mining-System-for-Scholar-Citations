import requests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"
}
proxies = {
    "http": "socks4://98.162.25.7:31653",
    "https": "socks4://98.162.25.7:31653",
}

url = "https://www.google.com/search?q=python"

res = requests.get(url, headers=headers)
print(res)
res = requests.get(url, headers=headers, proxies=proxies)
print(res)
