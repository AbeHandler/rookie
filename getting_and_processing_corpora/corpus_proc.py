import csv
import json
import sys
import os

from stanford_corenlp_pywrapper import CoreNLP
proc = CoreNLP("pos", corenlp_jars=[sys.argv[1] + '/*'])

try: 
    os.remove('corpora/' + sys.argv[2] + '/processed/all.json')
except:
    pass

with open ("corpora/" + sys.argv[2] + "/raw/all.extract") as raw:
    for line in csv.reader(raw, delimiter="\t"):
        out = {}
        pubdate = line[1]
        headline = line[4]
        text = proc.parse_doc(line[5])
        out["pubdate"] = pubdate
        out["headline"] = headline
        out["text"] = text
        with open('corpora/' + sys.argv[2] + '/processed/all.json', 'a') as outfile:
            json.dump(out, outfile)
            outfile.write("\n")
