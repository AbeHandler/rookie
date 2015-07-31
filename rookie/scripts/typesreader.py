import itertools
import pickle
import pdb
from Levenshtein import distance as dist
from rookie.utils import get_pickled
from rookie import files_location

types = get_pickled("types.p")


def find_aliases(type_alias, input_items):
    return_array = []
    tmp = [k for k, v in input_items.items() if v == type_alias and k.split(" ") > 1]
    tmp = [o for o in tmp if len(o.split(" ")) > 1]

    for i in itertools.product(tmp, tmp):
        if (i[0] in i[1] or i[1] in i[0] or dist(i[1], i[0]) < 2) and i[0] != i[1]:
            return_array.append(i)
    return return_array


def get_types():
    output = {}

    for t in types.keys():
        tdict = types[t]
        try:
            ngrams = float(tdict['ngram'])
            tot = float(sum(v for k, v in tdict.items()))
            pctg = ngrams / tot
            if pctg < .9 and sum(v for k, v in tdict.items() if k != 'ngram') > 1:
                output[t] = max(tdict, key=tdict.get)
            else:
                output[t] = 'ngram'
        except KeyError:
            pctg = 0
    return output

types_processed = get_types()
pickle.dump(types_processed, open(files_location + "types_processed.p", "wb"))
person = find_aliases("PERSON", types_processed)
organization = find_aliases("ORGANIZATION", types_processed)