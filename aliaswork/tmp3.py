import sys
from rookie import log
from itertools import product
from Levenshtein import distance


def overlap(one, two):
    for pair in product(one.split(" "), two.split(" ")):
        if pair[0] == pair[1]:
            return True
        if pair[1] == pair[0]:
            return True
        if distance(pair[1], pair[0]) < 3:
            return True
        if distance(pair[0], pair[1]) < 3:
            return True
    return False


if __name__ == "__main__":

    terms = sys.argv[1]

    one, two = terms.split(",")

    if overlap(one, two):
        print "'" + one + "," + two + "'"
