import csv
import json
import sys
import os
import fstphrases

from stanford_corenlp_pywrapper import CoreNLP

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
parser.add_argument('--nlpjar', help='where is core nlp?', required=True)
parser.add_argument('--tagset', help='np fst tag set', required=False)
args = parser.parse_args()

proc = CoreNLP("pos", corenlp_jars=[args.nlpjar + '/*'])

try:
    os.remove('corpora/' + args.corpus + '/processed/all.anno_plus')
except:
    pass


if args.tagset is None:
    print "[*] using default tagset for npfst"


def get_phrases(tags, toks):
    '''extract phrases with npfst'''
    phrases = fstphrases.extract_from_poses(tags, 'NP', tagset=args.tagset)
    phrases_deets = []
    for phrase in phrases:
        # phrase = [0,1,2] (token positions)
        start = phrase[0]  # first token position
        end = phrase[len(phrase) - 1]  # last token position
        regular = toks[start: end + 1]  # to python slice
        regular = " ".join([o for o in regular]).strip()
        normalized = regular.lower()
        phrases_deets.append({"positions": phrase,
                              "regular": regular,
                              "normalized": normalized})
    return phrases_deets

def un_html_ify(text):
    """weird offset issues w/ core nlp. seems easiest to just replace"""
    return text # .replace("&amp;", "&").replace(u"-LSB-", "")

def sent_to_string(j_doc_sent):
    '''make string from jdoc sent'''
    output = []  ## list of unicode objects, both tokens and sometimes whitespace
    for tokno, tok in enumerate(j_doc_sent["tokens"]):
        tok_char_start = int(j_doc_sent["char_offsets"][tokno][0])
        if tokno > 0:
            prev_tok_char_end = int(j_doc_sent["char_offsets"][tokno - 1][1])
            if prev_tok_char_end < tok_char_start:
                output.append(u" ")
        assert isinstance(tok, unicode)
        output.append(tok)
    return u"".join(output)


with open ("corpora/" + args.corpus + "/raw/all.extract") as raw:
    count = 0
    for line in csv.reader(raw, delimiter="\t"):
        count += 1
        out = {}
        pubdate = line[1]
        headline = line[4]
        text = proc.parse_doc(un_html_ify(line[5]))
        try:
            url = line[6]
        except IndexError:
            url = "unknown"
        for ln in text["sentences"]:
            ln["as_string"] = sent_to_string(ln)
            ln["phrases"] = get_phrases(ln["pos"], ln["tokens"])
        out["pubdate"] = pubdate
        out["headline"] = headline
        out["text"] = text
        out["url"] = url
        with open('corpora/' + args.corpus + '/processed/all.anno_plus', 'a') as outfile:
            json.dump(out, outfile)
            outfile.write("\n")
