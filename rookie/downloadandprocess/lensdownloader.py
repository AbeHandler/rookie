from __future__ import print_function

import urllib2
import hashlib
import os

from bs4 import BeautifulSoup
from experiment import log
from experiment import CORPUS_LOC as corpus_loc

DOMAINLIMITED = "thelensnola.org"


def get_page(url):
    hash_url = hashlib.sha224(url).hexdigest()
    url_file = corpus_loc + hash_url
    if os.path.exists(url_file):
        log.info("already have " + url)
        html = "".join([i for i in open(url_file)])
    else:
        log.info("downloading " + url)
        headers = {'User-Agent': "Abe Handler: urllib2"}
        req = urllib2.Request(url, headers=headers)
        con = urllib2.urlopen(req)
        html = con.read()
        with open(url_file, 'w') as openfile:
            print(html, file=openfile)
    return html


def get_html_summary(i):
    htmls = []
    i = str(i)
    url = "http://thelensnola.org/page/" + i + "/?s="
    htmls.append(get_page(url))
    log.info('Downloading summary | {}'.format(i))
    return htmls


def get_urls_from_summary(html):
    urls = []
    soup = BeautifulSoup(html)
    h3 = soup.find_all('h3')
    for i in h3:
        try:
            if "Permalink" in i.contents[0].attrs['title']:
                url = i.contents[0].attrs['href']
                urls.append(url.strip("/"))
        except AttributeError:  # can skip elements that don't have hrefs
            pass
        except KeyError:  # not a link. does not have a title
            pass
    return urls


def get_all_urls():
    url_output = []
    for i in range(1, 435):
        summary = get_html_summary(i)
        for html in summary:
            urls = get_urls_from_summary(html)
            for url in urls:
                url_output.append(url)
    return url_output


if __name__ == '__main__':
    urls = get_all_urls()
    for url in urls:
        try:
            page = get_page(url)
        except:
            pass
