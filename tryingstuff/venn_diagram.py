import pdb
import json
import itertools
from collections import defaultdict
from whooshy.reader import query_whoosh, query_subset

counter = defaultdict(int)

cooccurances = defaultdict(int)

query = "Mitch Landrieu"

query_back = query_whoosh(query, aliases=True, top_n=3)

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
                    subset = query_subset(results, facet[0], term_type)
                    output[facet[0]] = subset
                    break
        except KeyError:
            pass

pick_facets()
combos = [i for i in itertools.product(output, output)]

combos.append(set(output.keys()))


for key in output:
    for otherkey in output:
        cooccurances["m" + key] += 1
        try:
            subset = output[key]
            for i in subset:
                docid = i[0]
                docdict = i[1]
                for thing in docdict:
                    items = docdict[thing]
                    if otherkey in items:
                        cooccurances[key + "-" + otherkey] += 1
        except KeyError:
            pass


with open('cooccurances.tmp', 'w') as outfile:
    json.dump(dict(cooccurances), outfile)

