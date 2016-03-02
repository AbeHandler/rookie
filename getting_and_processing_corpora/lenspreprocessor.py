import html2text
import hashlib
import os
import json
import sys
import glob
import ipdb
import csv
import re
from datetime import datetime
from bs4 import BeautifulSoup

from stanford_corenlp_pywrapper import CoreNLP
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



def process_story(html):
    try:
        if '<span class="opinion-label">Opinion</span>' in html:
            # skip. opinion
            return {}
        if "category-what-were-reading" in html:
            # "what were reading. skip"
            return {}
        soup = BeautifulSoup(html)
        full_text = repr(soup.select(".entry-content")[0])
        url = re.search("http://.{1,}\)", soup.select(".print-header")[0].get_text()).group(0)[:-1]
        full_text = full_text.decode('ascii', 'ignore')
        h = html2text.HTML2Text()
        h.body_width = 0
        h.ignore_links = True
        full_text = h.handle(full_text)
        return {"pubdate": get_pub_date(soup), "headline": soup.select(".entry-title")[0].text, "text": full_text, "url": url}
    except ValueError:
        print 'ValueError'
        return {}
    except IndexError:
        print 'IndexError'
        return {}
    except OSError:
        print 'OSError'
        return {}


def get_page(url):
    headers = {'User-Agent': "Abe Handler: urllib2"}
    req = urllib2.Request(url, headers=headers)
    con = urllib2.urlopen(req)
    html = con.read()
    return html


try:
    os.remove("corpora/lens/raw/all.json")
except OSError:
    pass

proc = CoreNLP("pos", corenlp_jars=["/Users/ahandler/research/nytweddings/stanford-corenlp-full-2015-04-20/*"])


files = glob.glob("corpora/lens/raw/html/lens_processed/*")
print len(files)
for f in files:
    with open(f) as inf:
        html = "\n".join(inf.readlines())
        structured_story = process_story(html)
        if len(structured_story.keys()) > 0:
            with open("corpora/lens/raw/all.json", "a") as outf:
                outwriter = csv.writer(outf, delimiter='\t', quotechar='"')
                try:
                    outwriter.writerow(["", structured_story["pubdate"], "","", structured_story["headline"], proc.parse_doc(structured_story["text"]), structured_story["url"]])
                except UnicodeEncodeError:
                    print "unicode error"
                    pass