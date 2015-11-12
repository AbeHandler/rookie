import pdb
import json
import sys
import itertools
from collections import defaultdict
from rookie.utils import get_document_frequencies
from whooshy.reader import query_whoosh, query_subset
from experiment.models import get_metadata_file

counter = defaultdict(int)

cooccurances = defaultdict(int)

mt = get_metadata_file()

query = "coastal restoration"

query_back = query_whoosh(query)

results = query_back[0]

org = [i for i in query_back[1]["organizations"]]
ppl = [i for i in query_back[1]["people"]]
ngram = [i for i in query_back[1]["terms"]]

keys = ['people', 'ngram', 'org']
facets = defaultdict(lambda: defaultdict(int))

for result in results:
    if "Bobby Jindal" in mt[result]["people"]:
        for key in keys:
#             if key == "org":
#                pdb.set_trace()
            for i in mt[result][key]:
                facets[key][i] += 1

people_df = get_document_frequencies("people")
orgs_df = get_document_frequencies("orgs")
ngrams_df = get_document_frequencies("ngrams")

facets['people'] = [(k, v) for k,v in facets['people'].items()]
facets['orgs'] = [(k, v) for k,v in facets['org'].items()]
facets['ngrams'] = [(k, v) for k,v in facets['ngram'].items()]

words = []


for facet in facets["people"]:
    itm = int(people_df[facet[0]] * facet[1])
    words.append((itm,facet[0]))

for facet in facets["orgs"]:
    itm = int(orgs_df[facet[0]] * facet[1])
    words.append((itm,facet[0]))
        
for facet in facets["ngrams"]:
    itm = int(ngrams_df[facet[0]] * facet[1])
    words.append((itm,facet[0]))

words = [w for w in words if w[0] > 0.]
words.sort()

with open("q=coastalrest##f=bobbyjindal", "w") as outf:
    for w in words:
        outf.write(str(w[0]) + "," + w[1] + "\n")