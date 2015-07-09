import glob
import json
import csv
import itertools
import os
import pdb
from rookie.classes import Document
from rookie import processed_location
from rookie.classes import NPEPair
from collections import defaultdict
from rookie import files_location

npe_counts = defaultdict(int)

joint_counts = defaultdict(int)

instances = defaultdict(set)

base = files_location

to_delete = 'joint_counts.csv', 'instances.csv', 'counts.csv'


def attempt_delete(filename):
    try:
        os.remove(base + filename)
    except OSError:
        pass


def filter_to_file(val):
    if type(val) is int:
        if int(val) > 5:
            return True
    if type(val) is set:
        return True
    return False


def write_count_to_file(filename, defaultdict):
    for k in defaultdict.keys():
        if filter_to_file(defaultdict[k]):
            with open(filename, 'a') as countsfile:
                writer = csv.writer(countsfile, delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
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
                sentence_counter = sentence_counter + 1
                gramner = sentence.gramners
                npe_product = set(itertools.product(gramner, gramner))
                stufffs = [i for i in npe_product]
                pairs = [NPEPair(i[0], i[1]) for i in npe_product]
                pairs = set(pairs)
                for pair in pairs:
                    npe_counts[repr(pair.word1)] += 1
                    npe_counts[repr(pair.word2)] += 1
                    instances[repr(pair.word1)].update((pair.word1.window, url))
                    instances[repr(pair.word2)].update((pair.word2.window, url))
                    joint_counts[(repr(pair.word1), repr(pair.word2))] += 1
        except UnicodeEncodeError:
            pass
        except KeyError:
            pass
        except TypeError:
            pass
        except ValueError:
            pass

write_count_to_file(base + "instances.csv", instances)
write_count_to_file(base + "counts.csv", npe_counts)
write_count_to_file(base + "joint_counts.csv", joint_counts)
