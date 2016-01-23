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

with open ("corpora/" + args.corpus + "/raw/all.extract") as raw:
    count = 0
    for line in csv.reader(raw, delimiter="\t"):
        count += 1
        out = {}
        pubdate = line[1]
        headline = line[4]
        text = proc.parse_doc(line[5])
        url = text = proc.parse_doc(line[6])
        out["pubdate"] = pubdate
        out["headline"] = headline
        out["text"] = text
        with open('corpora/' + args.corpus + '/processed/all.json', 'a') as outfile:
            json.dump(out, outfile)
            outfile.write("\n")
