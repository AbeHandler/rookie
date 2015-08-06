import pdb
import collections
from rookie.utils import get_pickled

TOTAL_WINDOWS = 12098  # printed out from tmp2 counter

windows = get_pickled("pickled/people_windows.p")
window_counts = get_pickled("pickled/people_gram_df.p")
total_counts = sum([v for k, v in window_counts.items()])


def tfidf(term):
    return term[1] * window_counts[term[0]]

for key in windows.keys():
    itemz = collections.Counter(windows[key]).items()
    things = [i for i in itemz if i[1] > 1]
    if len(things) > 0:
        print key, things

pdb.set_trace()

# landrieu = [(i, tfidf(i)) for i in collections.Counter(windows['Susan Guidry']).items() if i[1] > 1]

# landrieu.sort(key=lambda x: x[1], reverse=True)

# print landrieu[0:5]