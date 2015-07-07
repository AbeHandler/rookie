import string
import collections
import json
import re
from nltk.corpus import stopwords
from rookie.classes import EntityCount
import datetime


def get_pmi():
    with (open("pmis.json", "r")) as rw:
        pmis = json.load(rw)
        for key in pmis:
            pmis[key].sort(key=lambda x: x[1], reverse=True)
    return pmis


def clean_whitespace(full_text):
    pattern = re.compile("\ {2,}")  # clean any big spaces left over
    full_text = pattern.sub(" ", full_text)  # replace w/ small spaces
    return full_text


def get_stopwords():
    temp = stopwords.words("english")
    temp = temp + ['new', 'orleans', 'said', 'would', 'city', 'state',
                   'parish', 'louisiana', '', '|', 'said', 'say', 'story',
                   'we', 'cover', 'lens']
    return temp


def time_stamp_to_date(timestamp):
    timestamp = timestamp.split(" ")[0]
    yr = int(timestamp.split("-")[0])
    mo = int(timestamp.split("-")[1])
    dy = int(timestamp.split("-")[2])
    return datetime.date(yr, mo, dy)


def get_timestamps(name, type_entity, results):
    timestamps = [time_stamp_to_date(r['_source']['timestamp']) for r in
                  results if name
                  in r['_source']['entities'][type_entity]]
    return timestamps


def get_entity_counts(entities, etype, results):
    ents = [EntityCount(e) for e in
            collections.Counter(entities[etype]).most_common(25)]
    for e in ents:
        e.timestamps = get_timestamps(e.name, etype, results)
    return ents


def clean_punctuation(input_string):
    '''
    Assumes ASCII input. TODO: Error handling.
    '''
    for punctuation in string.punctuation:
        input_string = input_string.replace(punctuation, " ")
    return input_string
