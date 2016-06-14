'''
This module loads documents into whoosh and creates a sentence index
'''
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh import writing
from collections import defaultdict
import csv
import os
import sys
import ctypes
from itertools import tee, izip, islice, chain
csv.field_size_limit(sys.maxsize)
import ipdb
import ujson
import argparse
from dateutil.parser import parse


'''build connection to db'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp import CONNECTION_STRING
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()


def getcorpusid():
    go = lambda *args: session.connection().execute(*args)
    for i in go("select corpusid from corpora where corpusname='{}'".format(args.corpus)):
        return i[0]


def stop_word(w):
    return False # TODO: corpus specific stop words


def create_pubdate_index(metadata):
    '''
    Takes a dict of ngrams that shows which ngram in what pubdate.
    Inserts into db.
    '''
    go = lambda *args: session.connection().execute(*args)

    print "building pubdate index of len {}".format(str(len(metadata)))
    # string to pubdate matrix created in building matrix
    for i, ngram in enumerate(metadata):
        if i % 10000 == 0:
            sys.stdout.write(str(i) + "\t")
        dates = metadata[ngram]
        dates = sorted(set(dates))
        go(u"""INSERT INTO ngram_pubdates (ngram, pubdates, CORPUSID) VALUES (%s, %s, %s)""",
                ngram, ujson.dumps(dates), CORPUSID)

    print "\nindexing"
    go("create index on ngram_pubdates (ngram)")
    print "pubdate index built over %s terms" % (go("select count(1) from ngram_pubdates").fetchone()[0])


def load(index_location, processed_location):
    '''
    Load documents from procesed location into whoosh @ index_location
    '''

    s_counter = 0 # only increments when doc actually added to whoosh
    # w/o this kludge, doc ids cause index errors b/c loop counter higher b/c ~15 docs error on load

    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    ix = create_in(index_location, schema)
    writer = ix.writer()

    ngram_pubdate_index = defaultdict(list)

    go = lambda *args: session.connection().execute(*args)
    go('delete from doc_metadata where corpusid={}'.format(CORPUSID))
    go('delete from sentences_preproc where corpusid={}'.format(CORPUSID))
    session.commit()
    with open("corpora/{}/processed/all.anno_plus".format(args.corpus), "r") as raw:
        for ln, line in enumerate(raw):
            line_json = ujson.loads(line.replace("\n", ""))
            headline = line_json["headline"]
            pubdate = parse(line_json["pubdate"])
            procesed_text = line_json["text"]

            try:
                url = line_json["url"]
            except KeyError:
                url = "unknown"

            full_text = " ".join(t for s in line_json["text"]["sentences"]
                                 for t in s["tokens"])
            ngrams = []
            for sent in line_json["text"]["sentences"]:
                ngrams = ngrams + [o["regular"] for o in sent["phrases"]]

            def make_dict(sent):
                '''
                Make a token dictionary to store as json
                '''
                toks = [(tok, tokno, sent["char_offsets"][tokno]) for
                        tokno, tok in enumerate(sent["tokens"])]

                def sent_to_string(j_doc_sent):
                    '''make string from jdoc sent'''
                    # list of unicode objects, both tokens and sometimes whitespace
                    output = []
                    for tokno, tok in enumerate(sent["tokens"]):
                        tok_char_start = int(sent["char_offsets"][tokno][0])
                        if tokno > 0:
                            prev_tok_char_end = int(sent["char_offsets"][tokno - 1][1])
                            if prev_tok_char_end < tok_char_start:
                                output.append(u" ")
                        assert isinstance(tok, unicode)
                        output.append(tok)
                    return u"".join(output)

                raw = sent_to_string(sent)

                return {"as_string": raw,
                        "as_tokens": toks,
                        "unigrams": sent["tokens"]}

            sentences = [make_dict(sen) for sen in
                        line_json["text"]["sentences"]]
            preprocsentences = "###$$$###".join([sen["as_string"] for sen
                                                in sentences])
            if len(headline) > 0 and len(full_text) > 0:
                writer.add_document(title=headline, path=u"/" + str(s_counter),
                                    content=full_text)
                per_doc_json_blob = {'headline': headline,
                                    'pubdate': pubdate.strftime('%Y-%m-%d'),
                                    'ngrams': ngrams,
                                    "url": url,
                                    "sentences": sentences}
                go("""INSERT INTO doc_metadata (docid, data, corpusid) VALUES (%s, %s, %s)""", s_counter, ujson.dumps(per_doc_json_blob), CORPUSID)
                go("""INSERT INTO sentences_preproc (corpusid, docid, delmited_sentences) VALUES (%s, %s, %s)""", CORPUSID, s_counter, preprocsentences)
                for ngram in ngrams:
                    ngram_pubdate_index[ngram].append(pubdate.strftime('%Y-%m-%d'))
                s_counter += 1
                if s_counter % 1000==0:
                    sys.stdout.write("...%s" % s_counter); sys.stdout.flush()
        create_pubdate_index(ngram_pubdate_index)
        writer.commit(mergetype=writing.CLEAR)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
    args = parser.parse_args()

    CORPUSID = getcorpusid()

    print "adding {} to whoosh and checking ngrams".format(args.corpus)

    directory = "indexes/" + args.corpus
    if not os.path.exists(directory):
        os.makedirs(directory)
    load(directory, args.corpus)
    session.commit()
