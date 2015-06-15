import ner
import json
import glob


to_process = glob.glob('/Volumes/USB 1/lens_processed/*')


def get_full_text(data):
    sentences = data['lines']['sentences']
    full_text = []
    for sentence in sentences:
        full_text = full_text + sentence['lemmas']
    return " ".join(full_text).encode('ascii', 'ignore')


def get_doc_tokens(data):
    sentences = data['lines']['sentences']
    tokens = []
    for s in sentences:
        tokens = tokens + s['tokens']
    return tokens


def get_ner(data):
    tokens = get_doc_tokens(data)
    output = []
    sentences = data['lines']['sentences']
    for sentence in sentences:
        mentions = sentence['entitymentions']
        for m in mentions:
            token = " ".join(tokens[m['tokspan'][0]:m['tokspan'][1]])
            ner_type = m['type']
            output.append([token, ner_type])
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
            coref_group.append(" ".join(sentences[sentence]['tokens'][span[0]: span[1]]))
        groups.append(coref_group)
    return groups


def correct_ner(ner, corefs):
    for n in ner:
        for c in corefs:
            if n[0] in c and n[0] != c[0] and len(c[0]) < 30 and (str(n[1])=='ORGANIZATION' or str(n[1])=='PERSON'):
                n[0] = c[0]
    return ner


for p in to_process:
    try:
        with open(p, 'r') as processed:
            data = json.load(processed)
            full_text = get_full_text(data)
            url = data['url']
            timestamp = data['timestamp']
            links = data['links']
            links = data['headline']
            sentences = data['lines']['sentences']
            tokens = get_doc_tokens(data)
            ner = get_ner(data)
            corefs = get_co_references(data)
            new_ner = correct_ner(ner, corefs)
            print new_ner
    except ValueError:
        print 've'
    except TypeError:
        print 'te'
