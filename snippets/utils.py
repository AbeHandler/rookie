
import glob
import pdb
import pickle
from collections import defaultdict

from rookie.classes import IncomingFile

language_model = defaultdict(int)

files = glob.glob("/Users/abramhandler/research/rookie/data/lens_processed/*")

for fi in files:
    inf = IncomingFile(fi)
    try:
        tokens = inf.doc.full_text.split(" ")
        for t in tokens:
            language_model[t.lower()] += 1
    except AttributeError:
        pass

total_tokens = sum(v for k, v in language_model.items())

for key in language_model.keys():
    language_model[key] = float(language_model[key]) / float(total_tokens)

pickle.dump(language_model, open("lm.p", "wb"))
