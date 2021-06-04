# Comments-Mining-System-for-Scholar-Citations

Graduation project for undergraduates

## Installation

clone this repo into local disk.
```
git clone https://github.com/Phimos/Comments-Mining-System-for-Scholar-Citations
```

install citeminer with pip.
```
pip install -e .
```

**P.S.** Luminati is needed to crawl Google Scholar and other scholar webcites. https://luminati-china.biz/

## Usage

Use json config to determine the author / publication needed to be mined.

Change the config path in `pipeline.py`, and you can only run specific step if you want.

```
python pipeline.py
```

**P.S.** Sci-Hub will block the crawlers after about 10 times try. `download.sh` will retry every 5 minutes.

## TODO

Search `TODO` in code files, and you will find the TODO list. Some of them may be fixed soon.


## Useful Information

* Sci-Hub downloader
  https://github.com/zaytoun/scihub.py

* Google Scholar Crawler
  https://github.com/scholarly-python-package/scholarly

* Selenium Crawler template
  https://github.com/yeongbin-jo/python-selenium-crawler-template

* Python to Markdown
  https://github.com/mikrosimage/python-markup-writer

* Google Captcha Handler
  * https://2captcha.com

* Free Proxy
  * https://free-proxy-list.net
  * https://www.sslproxies.org
  * http://free-proxy.cz/en/
  * https://proxyscrape.com/free-proxy-list
  * https://www.proxynova.com/proxy-server-list
  * https://openproxy.space/list
  * https://www.proxyscan.io

