'''
Prepares data for aws cloud search
'''

import glob
import json
import pickle
import math
from rookie import files_location
from rookie.utils import get_pickled
from rookie.classes import IncomingFile
from collections import defaultdict
from rookie import processed_location

files_to_check = glob.glob(processed_location + "/*")

chuunks = 15

N = 0

doc_frequencies_people = defaultdict(int)
doc_frequencies_ngrams = defaultdict(int)
doc_frequencies_orgs = defaultdict(int)

counts = get_pickled("pickled/counts.p")
types_processed = get_pickled("pickled/types_processed.p")
keys = set(counts.keys())


def to_aws_format(infile, counter):
    upload = {}
    upload['type'] = 'add'
    upload['id'] = counter
    data = {}
    data['text'] = infile.doc.full_text
    data['headline'] = infile.headline
    data['url'] = infile.url
    data['pubdate'] = infile.pubdate

    # these last three might not be necessary.
    # TODO: rexamine. might slow down network
    data['people'] = [""] + [repr(p) for p in infile.doc.people]
    for p in data['people']:
        doc_frequencies_people[p] += 1
    data['organizations'] = [""] + [repr(p) for p in infile.doc.organizations]
    for o in data['organizations']:
        doc_frequencies_orgs[o] += 1
    grams = [""]
    for gram in infile.doc.ngrams:
        try:
            gram = str(" ".join([i.raw for i in gram]).upper())
            if gram in keys:
                grams.append(gram)
        except:
            print "unicode error"

    data['ngrams'] = grams
    for o in data['ngrams']:
        doc_frequencies_ngrams[o] += 1
    upload['fields'] = data
    return upload


output = []

datas = {}

file_counter = 0

chunks = 3

for i in range(0, chunks):
    datas[i] = []


def read_json(outfile):
    try:
        with (open(outfile, "r")) as infile:
            dat = json.load(infile)
            return dat
    except IOError:
        return []


def write_json(data, outfile):
    with (open(outfile, "w")) as output:
        dat = json.dump(data, output)


def caclulate_df(dictionary, N):
    output = {}
    for key in dictionary.keys():
        count = dictionary[key]
        output[key] = math.log(float(N) / float(count))
    return output

for counter in range(0, len(files_to_check)):
    N += 1
    arrayindex = len(files_to_check) % chunks
    infile = IncomingFile(files_to_check[counter])
    if (counter % 10) == 0:
        print counter
    if infile.doc is not None:
        aws_format = to_aws_format(infile, counter)
        datas[counter % chunks].append(aws_format)

for i in range(0, chunks):
    write_json(datas[i], "data/aws/" + str(i) + ".json")


doc_frequencies_ngrams.update((x, math.log(float(N) / float(y))) for x, y in doc_frequencies_ngrams.items())
doc_frequencies_people.update((x, math.log(float(N) / float(y))) for x, y in doc_frequencies_people.items())
doc_frequencies_orgs.update((x, math.log(float(N) / float(y))) for x, y in doc_frequencies_orgs.items())

pickle.dump(doc_frequencies_ngrams, open(files_location + "df_ngrams.p", "w"))
pickle.dump(doc_frequencies_people, open(files_location + "df_people.p", "w"))
pickle.dump(doc_frequencies_orgs, open(files_location + "df_orgs.p", "w"))
