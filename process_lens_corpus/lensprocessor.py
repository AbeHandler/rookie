from __future__ import print_function

import html2text
import hashlib
import os
import json
import sys

from datetime import datetime
from stanford_corenlp_pywrapper import sockwrap
from bs4 import BeautifulSoup
from rookie import log
from rookie import core_nlp_location
from rookie import processed_location
from rookie.downloadandprocess.lensdownloader import get_page


domainlimiter = "thelensnola"


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


def process_story_url(url, portno):
    try:
        portno = int(portno) + 12340
        log.info('running url {} on portno {}'.format(url, portno))
        hash_url = hashlib.sha224(url).hexdigest()
        if os.path.exists(processed_location + hash_url):
            print("Already processed {}".format(url))
            return
        proc = sockwrap.SockWrap("coref",
                                 corenlp_jars=[core_nlp_location],
                                 server_port=portno)
        json_text = {}
        log.info(url)
        html = get_page(url)
        if '<span class="opinion-label">Opinion</span>' in html:
            log.info("URL is opinion. Skipping {}".format(url))
            return
        if "category-what-were-reading" in html:
            log.info("URL is what we're reading. Skipping {}".format(url))
            return
        soup = BeautifulSoup(html)
        full_text = repr(soup.select(".entry-content")[0])
        full_text = full_text.decode('ascii', 'ignore')
        h = html2text.HTML2Text()
        h.body_width = 0
        h.ignore_links = True
        full_text = h.handle(full_text)
        json_text['timestamp'] = get_pub_date(soup)
        json_text['url'] = url
        json_text['headline'] = soup.select(".entry-title")[0].text
        # json_text['links'] = get_links(full_text)
        json_text['lines'] = proc.parse_doc(full_text)
        with open(processed_location + hash_url, "w") as hashfile:
            print(json.dumps(json_text), file=hashfile)
            log.info('Processed| {} into {}'.format(url, hash_url))
    except ValueError:
        log.info('ValueError| {} '.format(url))
    except IndexError:
        log.info('IndexError| {} '.format(url))
    except OSError:
        log.info('OSError| {} '.format(url))

process_story_url(sys.argv[1], sys.argv[2])