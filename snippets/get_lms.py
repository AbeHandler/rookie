
import glob
import pdb
import pickle
from collections import defaultdict

from experiment.classes import IncomingFile

language_model = defaultdict(int)
jk_language_model = defaultdict(int)

files = glob.glob("/Users/abramhandler/research/rookie/data/lens_processed/*")

counter = 0
for fi in files:
    print "{} of {}".format(counter, len(files))
    inf = IncomingFile(fi)
    try:
        tokens = inf.doc.full_text.split(" ")
        for ngram in inf.doc.ngrams:
            jk_language_model[" ".join([i.raw.lower() for i in ngram])] += 1
        for person in inf.doc.people:
            jk_language_model[str(person).lower()] += 1
        for org in inf.doc.organizations:
            jk_language_model[str(org).lower()] += 1

        for t in tokens:
            language_model[t.lower()] += 1
    except AttributeError:
        pass

total_tokens = sum(v for k, v in language_model.items())

for key in language_model.keys():
    language_model[key] = float(language_model[key]) / float(total_tokens)

total_tokens_jk = sum(v for k, v in jk_language_model.items())
for key in jk_language_model.keys():
    jk_language_model[key] = float(jk_language_model[key]) / float(total_tokens_jk)

pickle.dump(language_model, open("lm.p", "wb"))
pickle.dump(jk_language_model, open("jk_lm.p", "wb"))
