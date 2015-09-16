
import pdb
from experiment.cloud_searcher import query_cloud_search
from experiment.cloud_searcher import get_representitive_item
import itertools
from collections import defaultdict
from collections import Counter
import collections
import pickle

from experiment.simplemerger import Merger


stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'said', '$', 'would', ":", ".the", ",", "*"]

q = "coastal restoration"

results = [r for r in query_cloud_search(q)]

all1grams = []

for r in results:
    text = r['fields']['text'].lower()
    unigrams = text.split(" ")
    all1grams = all1grams + unigrams

all1grams = [i for i in all1grams if i not in stop_words]

allgramscounter = Counter(all1grams)

print "total ngrams: " + str(len(allgramscounter.keys()))
print allgramscounter.most_common(12)