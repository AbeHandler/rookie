'''
This module loads documents into whoosh and creates a sentence index
'''
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh import writing
from collections import defaultdict
from unidecode import unidecode
import csv
import os
import ipdb
import json
from tqdm import tqdm
import sys
import re
csv.field_size_limit(sys.maxsize)
import ujson
import phrasemachine
import argparse
from dateutil.parser import parse


import spacy
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe(nlp.create_pipe('sentencizer'))


def getcorpusid(corpus):
    with open("db/corpora_numbers.json", "r") as inf:
        dt = json.load(inf)
        assert corpus in dt.keys()
        return dt[corpus]


def load(index_location, processed_location):
    '''
    Load documents from procesed location into whoosh @ index_location
    '''

    s_counter = 0 # only increments when doc actually added to whoosh
    # w/o this doc ids cause index errors b/c loop counter higher b/c ~15 docs error on load

    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    ix = create_in(index_location, schema)
    writer = ix.writer()

    headlines_so_far = set()
    
    doc_metadata = {}
    sentences_preproc = {}

    with open("corpora/{}/processed/all.anno_plus".format(args.corpus), "r") as raw:
        for ln, line in enumerate(tqdm(raw)):
            # print ln
            try:
                line_json = ujson.loads(line.replace("\n", ""))
                try:
                    headline = line_json["headline"]
                except KeyError:
                    headline = "Headline: NA"

                try:
                    pubdate = parse(line_json["pubdate"])

                except ValueError: # sometimes throws typerror, other times value error. huh?
                    # nyt world news date format = 19870101_0000087
                    nytdate = re.match("[0-9]{8}(?=_)", line_json["pubdate"]).group(0)
                    assert len(nytdate) == 8
                    pubdate = parse(nytdate)
                except TypeError: 
                    # nyt world news date format = 19870101_0000087
                    nytdate = re.match("[0-9]{8}(?=_)", line_json["pubdate"]).group(0)
                    assert len(nytdate) == 8
                    pubdate = parse(nytdate)

                try:
                    url = line_json["url"]
                except KeyError:
                    url = "unknown"

                full_text = line_json["text"]

                doc = nlp(line_json["text"], disable=["parser", "ner"])

                tokens = [token.text for token in doc]
                pos = [token.pos_ for token in doc]

                ngrams = list(phrasemachine.get_phrases(tokens=tokens, postags=pos)['counts'].keys())

                ngrams = [unidecode(i) for i in ngrams]

                #sentences = line_json["text"]["sentences"]
                preprocsentences = "###$$$###".join([unidecode(str(i)) for i in doc.sents])

                def get_sent_phrases(toks, pos):
                    phrases = phrasemachine.get_phrases(tokens=tok_strings, postags=pos, output="token_spans")
                    out = []
                    for p in phrases['token_spans']:
                        start, end = p
                        regular = " ".join(toks[start:end])
                        normalized = regular.lower()
                        item = {"positions": range(start, end+1),
                                "regular": regular,
                                "normalized": normalized}
                        out.append(item)
                    return out

                sentences = []
                for s in doc.sents:
                    tok_strings = [str(i) for i in s]
                    toks = [t for t in s]
                    pos = [o.pos_ for o in toks]

                    sentences.append({"tokens": tok_strings,
                                      "phrases": get_sent_phrases(tok_strings, pos),
                                      "as_string": str(s)})

                if len(headline) > 0 and len(full_text) > 0 and headline not in headlines_so_far:
                    headlines_so_far.add(headline)
                    writer.add_document(title=headline, path=u"/" + str(s_counter),
                                        content=full_text)
                    per_doc_json_blob = {'headline': unidecode(headline),
                                         'pubdate': pubdate.strftime('%Y-%m-%d'),
                                         'ngrams': ngrams,
                                         "unigrams": tokens,
                                         "url": url,
                                         "sentences": sentences,
                                         "nsentences": sum(1 for i in doc.sents)}
                    
                    doc_metadata[s_counter] = ujson.dumps(per_doc_json_blob)
                    sentences_preproc[s_counter] = preprocsentences

                    with open("documents/{}-{}".format(CORPUS, s_counter), "w") as of:
                        out = {"sents": [i["as_string"] for i in sentences],
                               "headline": unidecode(headline)}
                        of.write(json.dumps(out))

                    s_counter += 1
            except UnicodeError:
                print("o")
        writer.commit(mergetype=writing.CLEAR)
        with open("db/{}.doc_metadata.json".format(args.corpus), "w") as of:
            of.write(json.dumps(doc_metadata))
        with open("db/{}.sentences_preproc.json".format(args.corpus), "w") as of:
            of.write(json.dumps(sentences_preproc))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
    args = parser.parse_args()

    CORPUSID = getcorpusid(args.corpus)
    CORPUS = args.corpus

    directory = "indexes/" + args.corpus
    if not os.path.exists(directory):
        os.makedirs(directory)
    load(directory, args.corpus)

