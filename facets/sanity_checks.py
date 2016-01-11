'''
This script just checks to see if the numpy matrixes created from build_matrix
actually reflect the metadata correctly using the trusted MT metadata
'''
from experiment.models import ROOKIE
from pylru import lrudecorator
import ujson
import ipdb
import cPickle as pickle

results = ROOKIE.query("Mitch Landrieu")

@lrudecorator(100)
def get_metadata_file():
    print "Loading metadata file"
    with open("rookieindex/meta_data.json") as inf:
        metadata = ujson.load(inf)
    return metadata

people_key = pickle.load(open("rookieindex/people_key.p", "rb"))
people_key_r = {v: k for k, v in people_key.items()}
people_matrix = pickle.load(open("rookieindex/people_matrix.p", "rb"))

MT = get_metadata_file()

def row_to_people():
    matrixed_ppl = [i for i,j in enumerate(people_matrix[:,r]) if j > 0]

for r in results:
    ppl = [p for p in set([str(p) for p in MT[r]["people"]])]
    matrixed_ppl = [people_key_r[i] for i,j in enumerate(people_matrix[:,r]) if j > 0]
    ppl.sort()
    matrixed_ppl.sort()
    for i in matrixed_ppl:
        assert i in ppl # all matrixed ppl should be in MT ppl. but not = b/c matrixed ppl is filtered
