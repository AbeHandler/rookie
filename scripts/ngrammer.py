import glob
import json
import collections
import pickle

from rookie import log
from rookie.utils import get_full_text
from rookie.utils import get_grams


# To do: just dumping out raw json is apparently faster than
# pickle and apparently you can get word ngrams way
# faster than nltk using just itertools. But like, not the point
# at this stage.

files = glob.glob("/Volumes/USB 1/lens_processed/*")


all_1 = []
all_2 = []
all_3 = []

for f in files:
    try:
        with open(f, "r") as data_file:
            log.info("adding|" + f)
            data = json.load(data_file)
            full_text = get_full_text(data)
            grams = get_grams(full_text)
            all_1 = all_1 + grams[0]
            all_2 = all_2 + [i for i in grams[1]]
            all_3 = all_3 + [j for j in grams[2]]
    except ValueError:
        pass


def write_grams(filename, grams):
    with open(filename, 'wb') as outfile:
        out = {}
        counter = collections.Counter(grams)
        for key in counter.keys():
            out[key] = counter[key]
        pickle.dump(out, outfile)


write_grams("data/3-grams.p", all_3)
write_grams("data/2-grams.p", all_2)
write_grams("data/1-grams.p", all_1)
