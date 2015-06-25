import json
import glob
import pdb
import pickle
from rookie.classes import N_Grammer
from rookie.utils import get_full_text
from rookie.utils import standardize_ner

TO_PROCESS = glob.glob('/Volumes/USB 1/lens_processed/*')

ENTITY_KEYS = ["TIME", "LOCATION", "ORGANIZATION",
               "PERSON", "MONEY", "NUMBER", "DATE"]

STOP_ENTITIES = ['Lens', 'The Lens', 'Matt Davis', 'Jessica Williams']

window_size = 10

windows = {}


def add_to_tally(entity, window):
    if entity in windows.keys():
        tmp = windows[entity]
        tmp.append(window)
        windows[entity] = tmp
    else:
        windows[entity] = [window]


def get_doc_tokens(data):
    sentences = data['lines']['sentences']
    tokens = []
    for s in sentences:
        tokens = tokens + s['tokens']
    return tokens


def get_ner(data):
    output = []
    sentences = data['lines']['sentences']
    for sentence in sentences:
        ner = sentence['ner']
        counter = 0
        while counter < len(ner):
            ne = ner[counter]
            if ne != "O" and ne in ENTITY_KEYS:
                ner_to_add = sentence['tokens'][counter]
                try:
                    while ner[counter + 1] == ne:
                        ne = ner[counter + 1]
                        counter = counter + 1
                        next_tok = sentence['tokens'][counter]
                        ner_to_add = ner_to_add + " " + next_tok
                except IndexError:
                    pass
                if ner_to_add not in STOP_ENTITIES:
                    output.append([ner_to_add, ne])
            counter = counter + 1
    return output


def get_co_references(data):
    entity_groups = data['lines']['entities']
    sentences = data['lines']['sentences']
    output = []
    for e in entity_groups:
        group = []
        if len(e['mentions']) > 1 and not e['mentions'] is None:
            for m in e['mentions']:
                group.append((m['sentence'], m['tokspan_in_sentence']))
        if len(group) > 0:
            output.append(group)
    groups = []
    for coref in output:
        coref_group = []
        for mention in coref:
            sentence = mention[0]
            span = mention[1]
            token = " ".join(sentences[sentence]['tokens'][span[0]: span[1]])
            coref_group.append(token)
        groups.append(coref_group)
    return groups


def correct_ner_to_first_mention(ner, corefs, full_text):
    for n in ner:
        for c in corefs:
            if n[0] in c and n[0] != c[0] and len(c[0]) < 30 and \
                      (str(n[1]) == 'ORGANIZATION' or str(n[1]) == 'PERSON'):
                n[0] = c[0]
    return ner


def correct_dates(ner, timestamp):
    output = []
    for n in ner:
        if n[1] == "DATE" and "XXXX" in n[0]:
            # if XXXX for yr, just guess pub year
            n[0] = n[0].replace("XXXX", timestamp)
            output.append([n[0], n[1]])
        else:
            output.append(n)
    return output


def dictionaryfy(entities):
    output = {}
    for key in ENTITY_KEYS:
        output[key] = []
    for entitiy in entities:
        output[entitiy[1]] = output[entitiy[1]] + [entitiy[0]]
    return output


def get_window(tokens, ner, window_size):
    # NOTE: these value errors show up when a token from the ner
    # is not in the outout. I think this is because the
    # tokens come from the lemmatized text, so not all tokens
    # in the ner will show up in the lemmas. given that the point
    # of this method is to pull ner from the window surround them,
    # I am just skipping when the ner is not in the window.
    # theoretically, there could be an issue if the ner gets lemmatized
    # into something else in the window -- but we'll see if that is really
    # an issue
    try:
        start_ner = tokens.index(ner.split(" ")[0])
        end_ner = start_ner + len(ner.split(" "))
        start = start_ner - window_size
        end = end_ner + window_size
    except ValueError:
        output = []
        return output

    # if start of window is before start of tokens, set to zero
    if start < 0:
        start = 0

    # if end of window is after end of tokens, set to len(tokens)
    if end > len(tokens):
        end = len(tokens)

    output = tokens[start: end]

    for token in ner.split(" "):
        try:
            output.remove(token)
        except ValueError:
            pass

    return output


def get_windows(process_file):
    try:
        output = {}
        with open(process_file, 'r') as processed:
            try:
                data = json.load(processed)
            except ValueError:
                print "no json could be decoded " + process_file
                return
            full_text = get_full_text(data)
            unigrams = full_text.split(" ")
            bigrams = N_Grammer(process_file).twograms
            trigrams = N_Grammer(process_file).threegrams
            tokens = full_text.split(" ")
            ner = get_ner(data)
            ner = correct_dates(ner, data['timestamp'][0:4])
            corefs = get_co_references(data)
            ner = correct_ner_to_first_mention(ner, corefs, full_text)
            ner = [[standardize_ner(n[0]), n[1]] for n in ner]
            ner = dictionaryfy(ner)
            for p in (ner['PERSON'] + ner['ORGANIZATION']):
                window = get_window(tokens, p, window_size)
                add_to_tally(p, window)
    except KeyError:
        print 'value error'


if __name__ == "__main__":
    for process_file in TO_PROCESS:
        try:
            get_windows(process_file)
            print len(windows.keys())
        except TypeError:
            pass
    with open("data/windows.p", "wb") as outfile:
        pickle.dump(windows, outfile)
