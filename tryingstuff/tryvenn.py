import pdb
import json
import sys
import itertools
from collections import defaultdict
from whooshy.reader import query_whoosh, query_subset

counter = defaultdict(int)

cooccurances = defaultdict(int)

query = sys.argv[1]

query_back = query_whoosh(query, top_n=3)

results = query_back[0]
aliases = query_back[1]['aliases']

output = {}

def get_metadata_file():
    with open("data/meta_data.json") as inf:
        metadata = json.load(inf)
    return metadata

mt = get_metadata_file()

def pick_facets():
    for term_type in query_back[1]:
        facets = [i for i in query_back[1][term_type]]
        facets.reverse()
        keep_looping = True
        try:
            for facet in facets:
                if len(set(facet[0].split(" ")).intersection(query.split(" "))) == 0:
                    subset = query_subset(results, facet, term_type)
                    print len(subset)
                    output[facet[0]] = subset
                    break
        except KeyError:
            pass

pick_facets()

combos = [i for i in itertools.product(output, output)]

combos.append(tuple(set(output.keys())))

to_check = ['people', 'ngram', 'org']

for combo in combos:
    need_to_find = set(combo)
    for result in results:
        all_terms = set([i for i in itertools.chain(*[mt[result][key] for key in to_check])])
        if need_to_find.issubset(all_terms):
            if len(need_to_find) > 1:
                cooccurances["-".join(need_to_find)] += 1
            elif len(need_to_find) == 1: # this will only fire on single cases
                cooccurances[need_to_find.pop()] += 1
# MAP IT

print output.keys()
print cooccurances

import json
import pdb
from matplotlib import pyplot as plt
import numpy as np
from matplotlib_venn import venn3, venn3_circles
plt.figure(figsize=(4,4))

counts = cooccurances

venndiag = {}

A, B, C = [i for i in counts.keys() if i.count("-")==0]

try:
    triple_intersect = counts[[i for i in counts.keys() if i.count("-")==2][0]]
except IndexError:
    triple_intersect = 0

venndiag["ABC"] = triple_intersect
venndiag["AB"] = counts[A +"-"+ B]
venndiag["BC"] = counts[B +"-"+ C]
venndiag["AC"] = counts[A +"-"+ C]
venndiag["A"] = counts[A]
venndiag["B"] = counts[B]
venndiag["C"] = counts[C]

# v = venn3(subsets=(1, 2, 3, 4, 5, 6, 7), set_labels = ('A', 'B', 'C'))
v = venn3(subsets=(venndiag['A'], venndiag['B'], venndiag['AB'], venndiag['C'], venndiag['AC'], venndiag['BC'], venndiag['ABC']), set_labels = (A, B, C))
plt.title(query)
# plt.annotate('Unknown set', xy=v.get_label_by_id('100').get_position() - np.array([0, 0.05]), xytext=(-70,-70),
#             ha='center', textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='gray', alpha=0.1),
#             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5',color='gray'))
plt.savefig(query)
    
    

