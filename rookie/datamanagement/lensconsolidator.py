import json
import glob

from rookie.utils import clean_punctuation
from elasticsearch import Elasticsearch

elasticsearch = Elasticsearch(sniff_on_start=True)

elasticsearch.indices.delete(index='*')

TO_PROCESS = glob.glob('/Volumes/USB/lens_processed/*')

ENTITY_KEYS = ["TIME", "LOCATION", "ORGANIZATION",
               "PERSON", "MONEY", "NUMBER", "DATE"]

STOP_ENTITIES = ['Lens', 'The Lens', 'Matt Davis', 'Jessica Williams']


def get_full_text(data):
    try:
        sentences = data['lines']['sentences']
        full_text = []
        for sentence in sentences:
            full_text = full_text + sentence['lemmas']
        full_text = " ".join(full_text).encode('ascii', 'ignore').lower()
        full_text = clean_punctuation(full_text)
        return full_text
    except TypeError:
        return ""


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


def correct_ner_to_first_mention(ner, corefs):
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


def add_to_elastic_search(process_file):
    try:
        output = {}
        with open(process_file, 'r') as processed:
            data = json.load(processed)
            output['full_text'] = get_full_text(data)
            output['url'] = data['url']
            output['timestamp'] = data['timestamp']
            output['links'] = data['links']
            output['headline'] = data['headline']
            sentences = data['lines']['sentences']
            tokens = get_doc_tokens(data)
            ner = get_ner(data)
            ner = correct_dates(ner, data['timestamp'][0:4])
            corefs = get_co_references(data)
            ner = correct_ner_to_first_mention(ner, corefs)
            output['entities'] = dictionaryfy(ner)
            res = elasticsearch.index(index="lens",
                                      doc_type='news_story',
                                      body=output)
    except ValueError:
        print 'value error'


if __name__ == "__main__":
    for process_file in TO_PROCESS:
        add_to_elastic_search(process_file)
