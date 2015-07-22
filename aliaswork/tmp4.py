import pdb
from Levenshtein import distance
from itertools import product
from rookie.utils import get_pickled

levenshteins = defaultdict(float)

vocab = get_pickled("unigrams.p").keys()

for i in itertools.product(vocab, vocab):
    print i
