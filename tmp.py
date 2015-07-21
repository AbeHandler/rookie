from itertools import product
from rookie import log
from rookie.features import Featureizer

keys = [i.replace("\n", "") for i in open('keys.csv')]

log.info(sum(1 for x in product(keys, keys)))

counter = 0
for key in product(keys, keys):
    counter = counter + 1
    if counter % 10000 == 0:
        log.info(counter)
    features = Featureizer.get_features(key[0], key[1])
    if (features['lidstone'] > 0 or features['levenshtein'] < 3) \
       and features['pmi_overlap'] > 0:
            print key
            print features
# print Featureizer.get_features("A. Shaw", "A. Shaw Elementary")
# print Featureizer.get_features("A. Capdau", "A. Capdau Charter")
