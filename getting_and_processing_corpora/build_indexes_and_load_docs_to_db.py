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
from tqdm import tqdm
import sys
import re
csv.field_size_limit(sys.maxsize)
import ujson
import phrasemachine
import argparse
from dateutil.parser import parse


'''build connection to db'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp import CONNECTION_STRING
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()


import spacy
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe(nlp.create_pipe('sentencizer'))


def getcorpusid():
    go = lambda *args: session.connection().execute(*args)
    for i in go("select corpusid from corpora where corpusname='{}'".format(args.corpus)):
        return i[0]


def stop_word(w):
    return False # TODO: corpus specific stop words


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
    go = lambda *args: session.connection().execute(*args)
    go('delete from doc_metadata where corpusid={}'.format(CORPUSID))
    go('delete from sentences_preproc where corpusid={}'.format(CORPUSID))
    session.commit()
    with open("corpora/{}/processed/all.anno_plus".format(args.corpus), "r") as raw:
        for ln, line in enumerate(tqdm(raw)):
            # print ln
            try:
                # ipdb.set_trace()
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

                if len(headline) > 0 and len(full_text) > 0 and headline not in headlines_so_far:
                    headlines_so_far.add(headline)
                    writer.add_document(title=headline, path=u"/" + str(s_counter),
                                        content=full_text)
                    per_doc_json_blob = {'headline': unidecode(headline),
                                         'pubdate': pubdate.strftime('%Y-%m-%d'),
                                         'ngrams': ngrams,
                                         "unigrams": tokens,
                                         "url": url,
                                         "sentences": ""}
                    go("""INSERT INTO doc_metadata (docid, data, corpusid) VALUES (%s, %s, %s)""", s_counter, ujson.dumps(per_doc_json_blob), CORPUSID)
                    go("""INSERT INTO sentences_preproc (corpusid, docid, delmited_sentences) VALUES (%s, %s, %s)""", CORPUSID, s_counter, preprocsentences)
                    #for ngram in ngrams:
                    #    ngram_pubdate_index[ngram].append(pubdate.strftime('%Y-%m-%d'))
                    s_counter += 1
            except UnicodeError:
                print("o")
        writer.commit(mergetype=writing.CLEAR)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
    args = parser.parse_args()

    CORPUSID = getcorpusid()

    #print "adding {} to whoosh and checking ngrams".format(args.corpus)

    directory = "indexes/" + args.corpus
    if not os.path.exists(directory):
        os.makedirs(directory)
    load(directory, args.corpus)
    session.commit()
