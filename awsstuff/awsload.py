'''
Prepares data for aws cloud search
'''

import glob
import json
import pdb
import os
import math
import sys
from rookie.classes import IncomingFile
from collections import defaultdict
from rookie import processed_location

files_to_check = glob.glob(processed_location + "/*")

chuunks = 15


def to_aws_format(infile, counter):
    upload = {}
    upload['type'] = 'add'
    upload['id'] = counter
    data = {}
    data['text'] = infile.doc.full_text
    data['headline'] = infile.headline
    data['url'] = infile.url
    data['pubdate'] = infile.pubdate
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


for counter in range(0, len(files_to_check)):
    arrayindex = len(files_to_check) % chunks
    infile = IncomingFile(files_to_check[counter])
    if infile.doc is not None:
        aws_format = to_aws_format(infile, counter)
        datas[counter % chunks].append(aws_format)

for i in range(0, chunks):
    write_json(datas[i], "data/aws/" + str(i) + ".json")
