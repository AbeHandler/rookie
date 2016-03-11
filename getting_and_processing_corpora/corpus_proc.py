import csv
import json
import sys
import os

from stanford_corenlp_pywrapper import CoreNLP

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
parser.add_argument('--nlpjar', help='where is core nlp?', required=True)
args = parser.parse_args()

proc = CoreNLP("pos", corenlp_jars=[args.nlpjar + '/*'])

try:
    os.remove('corpora/' + args.corpus + '/processed/all.json')
except:
    pass

def un_html_ify(text):
    """weird offset issues w/ core nlp. seems easiest to just replace"""
    return text.replace("&amp;", "&").replace(u"-LSB-", "")

with open ("corpora/" + args.corpus + "/raw/all.extract") as raw:
    count = 0
    for line in csv.reader(raw, delimiter="\t"):
        count += 1
        out = {}
        pubdate = line[1]
        headline = line[4]
        text = proc.parse_doc(un_html_ify(line[5]))
        try:
            url = line[6]
        except:
            url = "unknown"
        #import ipdb
        #if url == "http://thelensnola.org/2013/03/01/councilwoman-agrees-that-sheriff-needs-another-building-for-more-prisoners/":
        #   ipdb.set_trace()   
         
        out["pubdate"] = pubdate
        out["headline"] = headline
        out["text"] = text
        out["url"] = url
        with open('corpora/' + args.corpus + '/processed/all.json', 'a') as outfile:
            json.dump(out, outfile)
            outfile.write("\n")
