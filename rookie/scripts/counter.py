import glob
import json
import csv
import itertools
import os
import pdb
from rookie.classes import Document
from rookie.classes import NPE
from rookie import processed_location
from rookie.classes import NPEPair
from collections import defaultdict

npe_counts = defaultdict(int)

joint_counts = defaultdict(int)

to_delete = 'joint_counts.csv', 'instances.csv', 'counts.csv'


def attempt_delete(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def write_count_to_file(filename, defaultdict, unpackk=False):
    for k in defaultdict.keys():
        if int(defaultdict[k]) > 5:
            with open(filename, 'a') as countsfile:
                writer = csv.writer(countsfile, delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
                if type(k) is tuple:
                    bits = [i for i in k]
                    writer.writerow(bits + [defaultdict[k]])
                else:
                    writer.writerow([k, defaultdict[k]])

for filename in to_delete:
    attempt_delete(filename)


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
                    with open('instances.csv', 'a') as csvfile:
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
write_count_to_file("joint_counts.csv", joint_counts, True)
