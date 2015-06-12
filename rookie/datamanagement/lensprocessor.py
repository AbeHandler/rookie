from __future__ import print_function

import nltk.data
import hashlib
import os

from datetime import datetime
from stanford_corenlp_pywrapper import sockwrap
from bs4 import BeautifulSoup
from rookie import log
from rookie import core_nlp_location
from rookie import processed_location
from rookie.datamanagement.lensdownloader import get_all_urls
from rookie.datamanagement.lensdownloader import get_page

proc = sockwrap.SockWrap("coref", corenlp_jars=[core_nlp_location])

domainlimiter = "thelensnola"

ids = {}

counter = 1


def get_links(full_text):
    output = []
    for i in full_text.findChildren('a'):
        try:
            linkurl = i.attrs['href']
            if domainlimiter in linkurl:
                if "support-us" in linkurl or "about-us" in linkurl:
                    pass
                else:
                    output.append([i.text, i.attrs['href']])
        except KeyError:
            pass
    return output


def get_pub_date(soup):
    time = soup.select("time")[0]
    time = time.attrs["datetime"].split("T")[0]
    year, month, day = [int(y) for y in time.split("-")]
    pubdate = str(datetime(year, month, day))
    return pubdate


def process_story_url(url):
    try:
        hash_url = hashlib.sha224(url).hexdigest()
        if os.path.exists(hash_url):
            print("Already processed {}".format(url))
            return
        SENTENCE_TOKENIZER = nltk.data.load('tokenizers/punkt/english.pickle')
        json_text = {}
        log.info(url)
        html = get_page(url)
        soup = BeautifulSoup(html)
        full_text = soup.select(".entry-content")[0]
        json_text['timestamp'] = get_pub_date(soup)
        json_text['url'] = url
        json_text['headline'] = soup.select(".entry-title")[0].text
        json_text['links'] = get_links(full_text)
        full_text = full_text.text.encode('ascii', 'ignore')
        json_text['lines'] = proc.parse_doc(sentence)
        hash_url = hashlib.sha224(url).hexdigest()
        with open(processed_location + hash_url, "w") as hashfile:
            print(json_text, file=hashfile)

    except ValueError:
        log.info('ValueError| {} '.format(url))
    except IndexError:
        log.info('IndexError| {} '.format(url))
    except OSError:
        log.info('OSError| {} '.format(url))


if __name__ == '__main__':
    urls = get_all_urls()
    for url in urls:
        process_story_url(url)
