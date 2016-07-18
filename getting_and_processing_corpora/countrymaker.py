import json
import ipdb
import os
import argparse

parser = argparse.ArgumentParser(description='args')

ANNO_LOC = "/Users/ahandler/research/posphrases/py/anno/"

parser.add_argument('-country', action="store")

args = parser.parse_args()

country = args.country

BASE = '/Users/ahandler/research/rookie/corpora/'

try:
    os.makedirs(BASE + country)
    os.makedirs(BASE + country + "/processed")
    os.makedirs(BASE + country + "/raw")
except OSError:
    pass


def has_country(jdoc, country):
    '''does this document mention this country?'''
    for sent in jdoc["sentences"]:
        for tok in sent["tokens"]:
            if tok.lower() == country.lower():
                return True
    return False


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


def remove(fn):
    try:
        os.remove(fn)
    except OSError:
        pass


OUTF = BASE + "{}/processed/all.anno_plus".format(country)

remove(OUTF)

# nicaraguas is a list preprocessed w/ grep.
# could easily by a list of all anno files.
with open("fns", "r") as inf:
    for ln in inf:
        print country, ln
        fn = ln.replace("\n", "")
        if "anno_plus" in fn:
            with open(ANNO_LOC + "/" + fn, "r") as newf:
                for ln2 in newf:
                    pubdate = ln2.split("\t")[0]
                    dt = ln2.split("\t")[1]
                    jdoc = json.loads(dt)
                    out = {}
                    out["text"] = jdoc
                    for sen in out["text"]["sentences"]:
                        sen["as_string"] = sent_to_string(sen)
                    out["headline"] = "unknown"
                    out["url"] = "unknown"
                    out["pubdate"] = pubdate
                    if has_country(jdoc, country):
                        with open(OUTF, "a") as outf:
                            outf.write(json.dumps(out) + "\n")
