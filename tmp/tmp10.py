
import pdb
import glob
from experiment.cloud_searcher import query_cloud_search
from experiment.cloud_searcher import get_representitive_item
from experiment.cloud_searcher import get_overview
import itertools
from rookie.classes import IncomingFile
from collections import defaultdict
import collections
import pickle

def pairwise(self, iterable, n=2):
    return izip(*(islice(it, pos, None) for pos, it in enumerate(tee(iterable, n))))

def get_ngrams(self, words, n=2):
    words = [i for i in words if not stop_word(i.raw.upper())]
    return self.pairwise(words, n)

processed_location = "/Users/ahandler/research/rookie/data/lens_processed"

files_to_check = glob.glob(processed_location + "/*")

q = "coastal restoration"
term = "bobby jindal"

# results = [r for r in query_cloud_search(q)]

results = pickle.load(open("jindalqtmp", "r"))

pdb.set_trace()

has_term = []

for r in results:
    if term in r['fields']['text'].lower():
        has_term.append(r)

# pickle.dump(results, open("jindalqtmp", "w"))

urls = []

ngrams = []



for result in has_term:
	url = result['fields']['url']
	try:
		ngrams.append(result['fields']['ngrams'])
	except:
		pass
	urls.append(url)

totals = []
for nlist in ngrams:
    for n in nlist:
        totals.append(n)

pdb.set_trace()
checkthese = pickle.load(open("checkthesttmp", "r"))

'''
checkthese = []
for f in files_to_check:
	print f
	infile = IncomingFile(f)
	if infile.url in urls:
		checkthese.append(infile)
'''

jindals = []

for inf in checkthese:
	for sentence in inf.doc.sentences:
		if "jindal" in " ".join(i.raw for i in sentence.tokens).lower():
			jindals.append( " ".join(i.raw for i in sentence.tokens).lower())

pdb.set_trace()