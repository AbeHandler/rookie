import sys
from rookie import log
from rookie.features import Featureizer

terms = sys.argv[1]

one, two = terms.split(",")

features = Featureizer.get_features(one, two)
if (features['lidstone'] > .001 or features['levenshtein'] < 4) \
     and features['pmi_overlap'] > 0 and one != two:
        log.info("candidate|" + one + "," + two)
else:
    log.info("skip|" + one + "," + two)
