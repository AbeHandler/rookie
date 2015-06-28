import glob
import json
import collections
import pickle
from rookie import log
from rookie.classes import Document
from rookie.classes import N_Grammer
from rookie import processed_location

# To do: just dumping out raw json is apparently faster than
# pickle and apparently you can get word ngrams way
# faster than nltk using just itertools. But like, not the point
# at this stage.

files = glob.glob(processed_location)

all_2 = []
all_3 = []

counter = 0
for f in files:
    try:
        print counter
        counter = counter + 1
        with open(f, "r") as data_file:
            log.info("adding|" + f)
            data = json.load(data_file)['lines']
            document = Document(data)
            tokens = document.tokens
            ng = N_Grammer()
            grams = ng.get_syntactic_ngrams(tokens)
            bigrams = grams[0]
            trigrams = grams[1]
            all_2.extend(grams[0])
            all_3.extend(grams[1])
    except ValueError:
        pass
    except TypeError:
        pass


def write_grams(filename, grams):
    with open(filename, 'wb') as outfile:
        out = []
        raws = []
        for gram in grams:
            raws.append(" ".join([i.raw for i in gram]))
        counter = collections.Counter(raws)
        # filter those that only occur once
        for key in counter.keys():
            if counter[key] > 1:
                out.append((key, counter[key]))
        out.sort(key=lambda tup: tup[1])
        pickle.dump(out, outfile)


write_grams("data/3-grams.p", all_3)
write_grams("data/2-grams.p", all_2)
