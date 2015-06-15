import ner
import json
import glob
import re


TO_PROCESS = glob.glob('/Volumes/USB 1/lens_processed/*')


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
            if ner_type == 'ORDINAL' or ner_type == 'NUMBER':
                pass
            if ner_type == 'DATE':
                try:
                    valu = re.findall("value=\".+\"", m['timex_xml'])[0]
                    valu = valu.replace('value=', '').replace('"', "")
                    if not any(char.isdigit() for char in valu):
                        pass
                    elif "temporalFunction=true" in valu or "WXX" in valu:
                        pass
                    else:
                        output.append([valu, ner_type])
                except KeyError:
                    pass
            else:
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
    for n in ner:
        if n[1] == "DATE" and "XXXX" in n[0]:
            n[0] == timestamp  # if XXXX for yr, just guess pub year
    return ner


for process_file in TO_PROCESS:
    try:
        with open(process_file, 'r') as processed:
            data = json.load(processed)
            full_text = get_full_text(data)
            url = data['url']
            timestamp = data['timestamp']
            links = data['links']
            links = data['headline']
            sentences = data['lines']['sentences']
            tokens = get_doc_tokens(data)
            ner = get_ner(data)
            ner = correct_dates(ner, timestamp[0:4])
            corefs = get_co_references(data)
            new_ner = correct_ner_to_first_mention(ner, corefs)
            print new_ner
    except ValueError:
        print 've'
    except TypeError:
        print 'te'
