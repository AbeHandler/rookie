import glob
import json
import csv
import itertools
import os
import pdb
from rookie.classes import Document
from rookie.classes import NPE
from rookie import processed_location
from collections import defaultdict

npe_counts = defaultdict(int)

joint_counts = defaultdict(int)

to_delete = 'joint_counts.csv', 'graph.csv', 'counts.csv'


def attempt_delete(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def write_count_to_file(filename, defaultdict):
    for k in defaultdict.keys():
        if defaultdict[k] > 10:
            with open(filename, 'a') as countsfile:
                writer = csv.writer(countsfile, delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
                writer.writerow([k, defaultdict[k]])

for filename in to_delete:
    attempt_delete(filename)


class NPEPair(object):

    def __init__(self, word1, word2):
        self.word1 = repr(word1)
        self.word2 = repr(word2)

    def __eq__(self, other):
        if self.word1 == other.word1 and self.word2 == other.word2:
            return True
        elif self.word1 == other.word2 and self.word2 == other.word1:
            return True
        else:
            return False

    def __hash__(self):
        chars = [i for i in self.word1] + [i for i in self.word2]
        chars = tuple(sorted(chars))
        return chars.__hash__()

    def __repr__(self):
        return self.word1 + " " + self.word2

file_loc = processed_location

files_to_check = glob.glob(file_loc + "/*")

counter = 0

if __name__ == "__main__":
    for filename in files_to_check:
        try:
            counter = counter + 1
            if counter % 100 == 0:
                print str(counter)
            with (open(filename, "r")) as infile:
                json_in = json.loads(infile.read())
                url = json_in['url']
                pubdate = json_in['timestamp']
                data = json_in['lines']
            doc = Document(data)
            sentences = doc.sentences
            sentence_counter = 0
            for sentence in sentences:
                # print datetime.datetime.now()
                sentence_counter = sentence_counter + 1
                # print str(sentence_counter) + " of " + str(len(sentences))
                grams = []
                bigrams = sentence.bigrams
                trigrams = sentence.trigrams
                ner = sentence.ner
                for gram in bigrams:
                    grams.append(NPE(gram, gram[0].sentence_no))
                for gram in trigrams:
                    grams.append(NPE(gram, gram[0].sentence_no))
                npes = grams + ner
                npe_product = set(itertools.product(npes, npes))
                pairs = [NPEPair(i[0], i[1]) for i in npe_product]
                pairs = set(pairs)
                for pair in pairs:
                    with open('graph.csv', 'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',',
                                            quotechar='"',
                                            quoting=csv.QUOTE_MINIMAL)
                        writer.writerow([pair.word1, pair.word2, url, pubdate])
                        npe_counts[pair.word1] += 1
                        npe_counts[pair.word2] += 1
                        joint_counts[(pair.word1, pair.word2)] += 1
        except UnicodeEncodeError:
            pass
        except KeyError:
            pass
        except TypeError:
            pass
        except ValueError:
            pass

write_count_to_file("counts.csv", npe_counts)
write_count_to_file("joint_counts.csv", joint_counts)
