import csv
import json
import sys
import os

#import sys

#sys.path.append("stanford_corenlp_pywrapper/stanford_corenlp_pywrapper")

#import fstphrases

# from stanford_corenlp_pywrapper import CoreNLP
from tqdm import tqdm

import phrasemachine
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
#parser.add_argument('--nlpjar', help='where is core nlp?', required=True)
parser.add_argument('--tagset', help='np fst tag set', required=False)
args = parser.parse_args()

#proc = CoreNLP("pos", corenlp_jars=[args.nlpjar + '/*'])

try:
    os.remove('corpora/' + args.corpus + '/processed/all.anno_plus')
except:
    pass


if args.tagset is None:
    print("[*] using default tagset for npfst")


def get_phrases(tags, toks):
    '''extract phrases with npfst'''

    phrases2 = phrasemachine.get_phrases(tokens=toks, postags=tags, output='token_spans')['token_spans']

    phrases_deets = []
    for phrase in phrases2:
        # phrase = [0,1,2] (token positions)
        start = phrase[0]  # first token position
        end = phrase[1]
        regular = toks[start: end]  # to python slice
        regular = " ".join([o for o in regular]).strip()
        normalized = regular.lower()
        '''
        phrase
        (16, 17, 18, 19, 20)
        ipdb> regular
        u'today in a year-end speech'
        ipdb> normalized
        u'today in a year-end speech'
        '''
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
    import sys
    csv.field_size_limit(sys.maxsize)
    for line in tqdm(csv.reader(raw, delimiter="\t")):
        count += 1
        out = {}
        pubdate = line[1]
        headline = line[4]
        # text2 = nlp(un_html_ify(line[5]))

        #text = proc.parse_doc(un_html_ify(line[5]))

        try:
            url = line[6]
        except IndexError:
            url = "unknown"

        '''
        for sent in text2.sents:
            toks = [o for o in sent]
            import ipdb; ipdb.set_trace()
            ln["as_string"] = str(sent)
            ln["phrases"] = get_phrases(ln["pos"], ln["tokens"])
        '''
        out = {}
        out["pubdate"] = pubdate
        out["headline"] = headline
        out["text"] = un_html_ify(line[5])
        out["url"] = url
        with open('corpora/' + args.corpus + '/processed/all.anno_plus', 'a') as outfile:
            json.dump(out, outfile)
            outfile.write("\n")
