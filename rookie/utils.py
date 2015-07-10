import string
import json
import re
import datetime
import pdb
from rookie import files_location
from rookie import window_length
from pylru import lrudecorator


class Result(object):

    def __init__(self, string, pmi, windows):
        '''
        Initialize w/ the json output
        '''
        self.string = string
        self.pmi = pmi
        self.windows = windows
        self.id = string.__hash__()  # get ID from use in template

    def __repr__(self):
            return string


@lrudecorator(100)
def get_pmi():
    with (open(files_location + "pmis.json", "r")) as rw:
        pmis = json.load(rw)
        for key in pmis:
            pmis[key].sort(key=lambda x: x[1], reverse=True)
    return pmis


@lrudecorator(100)
def get_windows():
    with (open(files_location + "instances.json", "r")) as rw:
        windows = json.load(rw)
    return windows


@lrudecorator(100)
def get_window(term):
    windows = get_windows()
    tmp = windows[term]
    tmp.sort(key=lambda x: x[2])
    outout = []
    for t in tmp:
        try:
            index = t[1].index(term)
            left = t[1][:index][-window_length:]
            right = t[1][index + len(term):][:window_length]
            outout.append((t[2], left, term, right, t[0]))
        except ValueError:
            pass
    return outout


@lrudecorator(100)
def clean_whitespace(full_text):
    pattern = re.compile("\ {2,}")  # clean any big spaces left over
    full_text = pattern.sub(" ", full_text)  # replace w/ small spaces
    return full_text


@lrudecorator(100)
def time_stamp_to_date(timestamp):
    # example: 2011-01-10
    yr = int(timestamp.split("-")[0])
    mo = int(timestamp.split("-")[1])
    dy = int(timestamp.split("-")[2])
    return datetime.date(yr, mo, dy)


@lrudecorator(100)
def clean_punctuation(input_string):
    '''
    Assumes ASCII input. TODO: Error handling.
    '''
    for punctuation in string.punctuation:
        input_string = input_string.replace(punctuation, " ")
    return input_string
