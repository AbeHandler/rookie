from itertools import product
from rookie import log
from rookie.features import Featureizer

keys = [i.replace("\n", "") for i in open('keys.csv')]


def overlap(one, two):
    for pair in product(one.split(" "), two.split(" ")):
        if pair[0] in pair[1]:
            return True
        if pair[1] in pair[0]:
            return True
    return False


if __name__ == "__main__":
    counter = 0

    for key in product(keys, keys):
        counter = counter + 1
        if counter % 10000 == 0:
            log.info(counter)
        if key[0] == key[1]:
            pass
        else:
            if overlap(key[0], key[1]):
                print "'" + key[0] + "," + key[1] + "'"
