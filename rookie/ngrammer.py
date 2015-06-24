import json
import re

from itertools import tee, izip, islice


class N_Grammer(object):

    # https://stackoverflow.com/questions/21883108/fast-optimize-n-gram-implementations-in-python

    # valid_two_grams = ["NN", "AN"]
    # valid_three_grams = ["AAN", "NNN", "ANN"]

    # A = any adjective (PTB tag starts with JJ)
    # N = any noun (PTB tag starts with NN)

    def __init__(self, filename):
        with open(filename, 'r') as processed:
            data = json.load(processed)
            sentences = data['lines']['sentences']
            two_grams = []
            three_grams = []
            for sentence in sentences:
                grams = self.get_grams(sentence['parse'])
                two_grams = two_grams + grams[0]
                three_grams = three_grams + grams[1]
            self.twograms = two_grams
            self.threegrams = three_grams

    def is_adjective(self, t):
        if t[0:2] == "JJ":
            return True
        else:
            return False

    def is_noun(self, t):
        if t[0:2] == "NN":
            return True
        else:
            return False

    def pairwise(self, iterable, n=2):
        return izip(*(islice(it, pos, None) for pos, it
                      in enumerate(tee(iterable, n))))

    def zipngram2(self, words, n=2):
        return self.pairwise(words, n)

    def get_grams(self, s):
        p = "((?<=\()[A-Z]+ [^)^()]+(?=\)))"
        twograms = [i for i in self.zipngram2(re.findall(p, s))]
        twograms = [t for t in twograms if (self.is_adjective(t[0]) or
                    self.is_noun(t[0])) and self.is_noun(t[1])]
        twograms = [(t[0].split(" ")[1], t[1].split(" ")[1]) for t in twograms]

        threegrams = [i for i in self.zipngram2(re.findall(p, s), 3)]

        threegrams = [t for t in threegrams if self.is_noun(t[2]) and
                      (
                       (self.is_noun(t[1]) and self.is_noun(t[0])) or
                       (self.is_adjective(t[1]) and self.is_adjective(t[0])) or
                       (self.is_noun(t[1]) and self.is_adjective(t[0]))
                      )]
        threegrams = [(t[0].split(" ")[1], t[1].split(" ")[1],
                      t[2].split(" ")[1])
                      for t in threegrams]

        return (twograms, threegrams)
