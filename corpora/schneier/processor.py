'''
AH: Sep 3, 2018

This runs after scraper.py

It processes the output from the scraper into the format required by
the Rookie corpus injestion pipeline

'''

from goose3 import Goose
from bs4 import BeautifulSoup
from collections import defaultdict

import pickle
import json

with open("schneier.com", "rb") as inf:
    schneier = pickle.load(inf)

g = Goose()


def get_headline(article):
    '''example input => '<a name="12">Comments from Readers</a>'''
    headline = article.split("</h4>")[0]
    headline = BeautifulSoup(headline, 'html.parser').get_text()
    return headline  # e.g. Comments from Readers


def get_pubdate(url_page):
    '''example input => /crypto-gram/archives/2007/0315.html'''
    yyyy, mody = page.replace(".html","").split("/")[-2:]
    mo = mody[0:2]
    dy = mody[2:4]
    return "{}-{}-{}".format(yyyy, mo, dy)


with open("out.json", "w") as of:
    for page in schneier:
        for article in schneier[page].split('<h4>')[1:]:
            out = defaultdict()
            body = article.split("</h4>")[1]
            out["pubdate"] = get_pubdate(page)
            out["headline"] = get_headline(article)
            out["text"] = g.extract(raw_html=body).cleaned_text
            out["url"] = "https://www.schneier.com/" + page
            json.dump(out, of)
            of.write("\n")