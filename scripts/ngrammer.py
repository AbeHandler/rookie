import glob
import json
import collections

from rookie import log
from rookie.utils import get_full_text
from rookie.utils import get_grams


files = glob.glob("/Volumes/USB/lens_processed/*")

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

with open('data/3-grams', 'w') as outfile:
    out = {}
    counter = collections.Counter(all_3)
    for key in counter.keys():
        out[" ".join(key)] = counter[key]
    json.dump(out, outfile)

with open('data/2-grams', 'w') as outfile:
    out = {}
    counter = collections.Counter(all_2)
    for key in counter.keys():
        out[" ".join(key)] = counter[key]
    json.dump(out, outfile)

with open('data/1-grams', 'w') as outfile:
    out = {}
    counter = collections.Counter(all_1)
    for key in counter.keys():
        out[" ".join(key)] = counter[key]
    json.dump(out, outfile)
